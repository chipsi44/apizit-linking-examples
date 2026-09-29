const fs=require("node:fs");
const path=require("node:path");
const {execFileSync}=require("node:child_process");
const {sha256}=require("./docs.cjs");
const ROOT=path.resolve(__dirname,"..");
function expectedExport() {
    const catalog=JSON.parse(fs.readFileSync(path.join(ROOT,"docs/catalog.json"),"utf8"));
    const files=new Map();
    for(const file of ["catalog.json","llms-source.txt",...catalog.pages.map(p=>p.slug+".md")]) files.set(file,fs.readFileSync(path.join(ROOT,"docs",file)));
    for(const file of ["docs.cjs","docs-renderer.cjs"]) files.set(file,fs.readFileSync(path.join(ROOT,"scripts",file)));
    files.set("schema/apizit-linking-v1.schema.json",fs.readFileSync(path.join(ROOT,"schema/apizit-linking-v1.schema.json")));
    const sourceCommit=execFileSync("git",["-c","safe.directory="+ROOT.replaceAll("\\","/"),"rev-parse","HEAD"],{cwd:ROOT,encoding:"utf8"}).trim();
    const tracked=execFileSync("git",["-c","safe.directory="+ROOT.replaceAll("\\","/"),"status","--porcelain","--","docs","scripts","schema"],{cwd:ROOT,encoding:"utf8"}).trim();
    const provenance={version:1,source_repository:"https://github.com/chipsi44/apizit-linking-examples",source_commit:sourceCommit,source_dirty:Boolean(tracked),files:Object.fromEntries([...files].map(([name,data])=>[name,sha256(data)]))};
    files.set("provenance.json",Buffer.from(JSON.stringify(provenance,null,2)+"\n"));
    return files;
}
function exportDocs(website,check=false) {
    const websiteRoot=fs.realpathSync(website);
    if(!fs.existsSync(path.join(websiteRoot,"scripts/build-static.cjs"))) throw new Error("Target is not an APIZIT website checkout.");
    const target=path.resolve(websiteRoot,"content/linking");
    if(!target.startsWith(websiteRoot+path.sep) || path.relative(websiteRoot,target)!==path.join("content","linking")) throw new Error("Unsafe documentation export target.");
    const files=expectedExport();
    if(check) {
        const actual=[];
        function visit(dir) { for(const item of fs.readdirSync(dir,{withFileTypes:true})){const file=path.join(dir,item.name);if(item.isSymbolicLink())throw new Error("Export cannot contain symlinks.");if(item.isDirectory())visit(file);else actual.push(path.relative(target,file).split(path.sep).join("/"));} }
        if(!fs.existsSync(target))throw new Error("Documentation export is absent.");
        visit(target);
        if(actual.sort().join("\n")!==[...files.keys()].sort().join("\n"))throw new Error("Documentation export file inventory differs.");
        for(const [file,data]of files) if(!fs.readFileSync(path.join(target,file)).equals(data)) throw new Error("Documentation export differs: "+file);
    } else {
        fs.rmSync(target,{recursive:true,force:true});
        for(const [file,data]of files){const out=path.join(target,file);fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,data);}
    }
    console.log((check?"Verified":"Exported")+" "+files.size+" files.");
}
if(require.main===module){const argv=process.argv.slice(2);const position=argv.indexOf("--website");if(position<0||!argv[position+1])throw new Error("Use --website /path/to/apizit-website [--check].");exportDocs(argv[position+1],argv.includes("--check"));}
module.exports={exportDocs,expectedExport};
