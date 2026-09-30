const assert=require("node:assert/strict");
const test=require("node:test");
const fs=require("node:fs");
const path=require("node:path");
const os=require("node:os");
const {renderMarkdown}=require("../scripts/docs-renderer.cjs");
const {readDocumentation,writeSupportFiles}=require("../scripts/docs.cjs");
const root=path.resolve(__dirname,"..");
test("agent indexes normalize Windows-authored source on every build host",()=>{
    const directory=fs.mkdtempSync(path.join(os.tmpdir(),"apizit-docs-index-"));
    try{
        const source=path.join(directory,"source"),output=path.join(directory,"output");
        fs.mkdirSync(source);fs.mkdirSync(output);
        fs.writeFileSync(path.join(source,"llms-source.txt"),"# Index\r\n\r\nWindows source\r\n");
        const documentation={catalog:{engine_version:"1.0.0rc1",release_channel:"candidate"},pages:[]};
        writeSupportFiles(output,source,documentation,"/linking/","https://test.apizit.com",path.join(root,"schema/apizit-linking-v1.schema.json"));
        const index=fs.readFileSync(path.join(output,"llms.txt"),"utf8");
        assert.ok(index.startsWith("# Index\n\nWindows source\n"));
        assert.ok(!index.includes("\r"));
    }finally{
        assert.equal(path.dirname(directory),os.tmpdir());
        assert.ok(path.basename(directory).startsWith("apizit-docs-index-"));
        fs.rmSync(directory,{recursive:true,force:true});
    }
});
test("the portable renderer escapes markup and retains explicit historical anchors",()=>{
    const {html,headings}=renderMarkdown('# Title\n\n<a id="choose"></a>\n\n## Choose\n\n| Signature | Meaning |\n| --- | --- |\n| `int \\| str` | Union |\n\n<script>bad()</script>');
    assert.equal((html.match(/id="choose"/g)||[]).length,1);
    assert.equal(headings[0].id,"choose");
    assert.match(html,/<code>int \| str<\/code>/);
    assert.ok(!html.includes("<script>"));
    for(const href of ["javascript:alert(1)","//evil.test/","/\\evil.test/"])assert.throws(()=>renderMarkdown("[bad]("+href+")"),/Unsafe/);
    assert.throws(()=>renderMarkdown("# Title\n\n## Same\n\n## Same"),/Duplicate/);
});
test("both publications render the same article and keep all former anchors",()=>{
    const source=readDocumentation(path.join(root,"docs"),"/apizit-linking-examples/","https://chipsi44.github.io");
    const target=readDocumentation(path.join(root,"docs"),"/linking/","https://test.apizit.com");
    assert.equal(source.pages.length,30);
    const isCandidate=/rc\d+$/.test(source.catalog.engine_version);
    assert.equal(source.catalog.release_channel,isCandidate?"candidate":"stable");
    const publishedCatalog=JSON.parse(fs.readFileSync(path.join(root,"site/catalog.json"),"utf8"));
    assert.equal(publishedCatalog.release_channel,source.catalog.release_channel);
    assert.ok(!fs.readFileSync(path.join(root,"site/llms.txt"),"utf8").includes("\r"));
    for(const [i,page] of source.pages.entries()){
        const normalized=page.html.replaceAll('href="/apizit-linking-examples/','href="/linking/');
        assert.equal(normalized,target.pages[i].html);
        const html=fs.readFileSync(path.join(root,"site",page.slug==="index"?"":page.slug,"index.html"),"utf8");
        assert.ok(html.includes(isCandidate?"Release candidate":"Stable release"));
        assert.ok(!html.includes(isCandidate?"Stable release":"Release candidate"));
        assert.equal(html.split("<article>")[1].split("</article>")[0],page.html);
        const download=fs.readFileSync(path.join(root,"site/markdown",page.slug+".md"),"utf8");
        assert.equal(download,page.markdown);
    }
    assert.ok(source.pages.find(p=>p.slug==="limits").html.includes('id="choose"'));
    for(const [slug,ids]of Object.entries(require("./legacy-anchors.json"))){
        const html=fs.readFileSync(path.join(root,"site",slug==="index"?"":slug,"index.html"),"utf8");
        for(const id of ids)assert.ok(html.includes('id="'+id+'"'),slug+"#"+id);
    }
});
