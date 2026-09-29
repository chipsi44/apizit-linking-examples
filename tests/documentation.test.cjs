const assert=require("node:assert/strict");
const test=require("node:test");
const fs=require("node:fs");
const path=require("node:path");
const {renderMarkdown}=require("../scripts/docs-renderer.cjs");
const {readDocumentation}=require("../scripts/docs.cjs");
const root=path.resolve(__dirname,"..");
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
    assert.equal(source.pages.length,23);
    for(const [i,page] of source.pages.entries()){
        const normalized=page.html.replaceAll('href="/apizit-linking-examples/','href="/linking/');
        assert.equal(normalized,target.pages[i].html);
        const html=fs.readFileSync(path.join(root,"site",page.slug==="index"?"":page.slug,"index.html"),"utf8");
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
