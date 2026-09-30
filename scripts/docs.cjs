const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const {renderMarkdown, escape} = require("./docs-renderer.cjs");

const sha256 = value => crypto.createHash("sha256").update(value).digest("hex");
const pagePath = slug => slug === "index" ? "" : slug + "/";
function materialize(markdown, basePath, origin = "") {
    return markdown.replaceAll("{{docs}}", basePath.replace(/\/$/, "")).replaceAll("{{origin}}", origin);
}
function readDocumentation(root, basePath, origin = "") {
    if (!/^\/(?:[a-z0-9-]+\/)+$/.test(basePath)) throw new Error("Invalid documentation prefix.");
    const catalog = JSON.parse(fs.readFileSync(path.join(root, "catalog.json"), "utf8"));
    if (catalog.version !== 1 || !/^\d+\.\d+\.\d+(?:rc\d+)?$/.test(catalog.engine_version) || catalog.pages[0]?.slug !== "index") throw new Error("Unsupported Linking documentation catalogue.");
    const seen = new Set();
    const pages = catalog.pages.map(page => {
        if (!/^[a-z0-9.-]+(?:\/[a-z0-9.-]+)*$/.test(page.slug) || page.slug.split("/").some(s => s === "." || s === "..") || seen.has(page.slug)) throw new Error("Invalid or duplicate documentation page.");
        seen.add(page.slug);
        const source = path.join(root, page.slug + ".md");
        if (fs.lstatSync(source).isSymbolicLink()) throw new Error("Documentation source cannot be a symbolic link.");
        const raw = fs.readFileSync(source, "utf8").replace(/\r\n/g, "\n");
        if (!raw.startsWith("# " + page.title + "\n")) throw new Error("Page title differs from catalogue: " + page.slug);
        const markdown = materialize(raw, basePath, origin);
        return {...page, markdown, ...renderMarkdown(markdown), url: basePath + pagePath(page.slug), markdownUrl: basePath + "markdown/" + page.slug + ".md", sha256: sha256(raw)};
    });
    return {catalog, pages};
}
function navigation(pages, basePath, currentSlug) {
    let group = "";
    return pages.map(page => {
        const label = page.group === group ? "" : '<p class="reading-group">' + escape(page.group) + "</p>";
        group = page.group;
        return label + '<a href="' + basePath + pagePath(page.slug) + '"' + (page.slug === currentSlug ? ' aria-current="page"' : "") + ">" + escape(page.title) + "</a>";
    }).join("");
}
function structuredData(page, catalog, baseUrl) {
    const url = new URL(pagePath(page.slug), baseUrl).href;
    const content = page.slug === "index"
        ? {"@type":"SoftwareApplication", name:"APIZIT Linking", applicationCategory:"DeveloperApplication", operatingSystem:"Cross-platform", softwareVersion:catalog.engine_version, programmingLanguage:"Python", license:"https://www.apache.org/licenses/LICENSE-2.0", downloadUrl:"https://pypi.org/project/apizit-linking/" + catalog.engine_version + "/", url, description:page.summary}
        : {"@type":"TechArticle", headline:page.title, description:page.summary, url, inLanguage:"en", dependencies:"APIZIT Linking " + catalog.engine_version, author:{"@type":"Organization",name:"APIZIT Linking maintainers"}};
    return {"@context":"https://schema.org","@graph":[content, {"@type":"BreadcrumbList",itemListElement:[{"@type":"ListItem",position:1,name:"APIZIT Linking",item:baseUrl}, ...(page.slug === "index" ? [] : [{"@type":"ListItem",position:2,name:page.title,item:url}])]}]};
}
function writeSupportFiles(outputRoot, sourceRoot, documentation, basePath, origin, schemaPath, sourceCommit = null) {
    const {catalog, pages} = documentation;
    const search = [];
    for (const page of pages) {
        const file = path.join(outputRoot, "markdown", page.slug + ".md");
        fs.mkdirSync(path.dirname(file), {recursive:true});
        fs.writeFileSync(file, page.markdown);
        search.push({title:page.title,url:page.url,text:page.summary + "\n" + page.markdown});
        for (const heading of page.headings) search.push({title:page.title + " · " + heading.title,url:page.url + "#" + heading.id,text:heading.title + "\n" + page.summary});
    }
    fs.mkdirSync(path.join(outputRoot, "schema"), {recursive:true});
    fs.copyFileSync(schemaPath, path.join(outputRoot, "schema/apizit-linking-v1.schema.json"));
    fs.writeFileSync(path.join(outputRoot, "search-index.json"), JSON.stringify(search));
    fs.writeFileSync(path.join(outputRoot, "catalog.json"), JSON.stringify({
        version:1,engine_version:catalog.engine_version,python_support:catalog.python_support,license:catalog.license,
        source_repository:"https://github.com/chipsi44/apizit-linking-examples",source_commit:sourceCommit,
        pages:pages.map(({slug,title,summary,group,url,markdownUrl,sha256})=>({slug,title,summary,group,url,markdown_url:markdownUrl,source_sha256:sha256}))
    },null,2) + "\n");
    const historical = materialize(fs.readFileSync(path.join(sourceRoot, "llms-source.txt"), "utf8"), basePath, origin);
    const index = "\n## Documentation pages and Markdown\n\n" + pages.map(page => "- [" + page.title + "](" + origin + page.markdownUrl + ")").join("\n") + "\n";
    fs.writeFileSync(path.join(outputRoot, "llms.txt"), historical + index);
}
module.exports = {readDocumentation, navigation, structuredData, writeSupportFiles, pagePath, sha256, materialize};
