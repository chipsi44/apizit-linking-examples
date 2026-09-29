const fs = require("node:fs");
const path = require("node:path");
const {execFileSync} = require("node:child_process");
const {readDocumentation, navigation, structuredData, writeSupportFiles, pagePath} = require("./docs.cjs");
const {escape} = require("./docs-renderer.cjs");
const ROOT = path.resolve(__dirname, "..");
const BASE = "/apizit-linking-examples/";
const ORIGIN = "https://chipsi44.github.io";
function buildDocs() {
    const output = path.resolve(ROOT, "site");
    if (path.dirname(output) !== ROOT || path.basename(output) !== "site") throw new Error("Unsafe documentation output.");
    fs.rmSync(output, {recursive:true,force:true});
    fs.mkdirSync(output, {recursive:true});
    const docs = readDocumentation(path.join(ROOT, "docs"), BASE, ORIGIN);
    fs.cpSync(path.join(ROOT,"docs/assets"),path.join(output,"assets"),{recursive:true});
    let commit = null;
    try { commit = execFileSync("git",["-c","safe.directory="+ROOT.replaceAll("\\","/"),"rev-parse","HEAD"],{cwd:ROOT,encoding:"utf8"}).trim(); } catch (_) { /* Fixture builds have no Git metadata. */ }
    writeSupportFiles(output,path.join(ROOT,"docs"),docs,BASE,ORIGIN,path.join(ROOT,"schema/apizit-linking-v1.schema.json"),commit);
    for (const page of docs.pages) {
        const url = ORIGIN + page.url;
        const title = page.title + " — APIZIT Linking";
        const html = '<!doctype html>\n<html lang="en" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">' +
            "<title>" + escape(title) + '</title><meta name="description" content="' + escape(page.summary) + '">' +
            '<link rel="canonical" href="' + url + '"><link rel="stylesheet" href="' + BASE + 'assets/docs.css">' +
            '<link rel="alternate" type="text/markdown" href="' + page.markdownUrl + '" title="Markdown version">' +
            '<meta property="og:type" content="' + (page.slug === "index" ? "website" : "article") + '"><meta property="og:site_name" content="APIZIT Linking">' +
            '<meta property="og:title" content="' + escape(title) + '"><meta property="og:description" content="' + escape(page.summary) + '"><meta property="og:url" content="' + url + '">' +
            '<meta property="og:image" content="' + ORIGIN + BASE + 'assets/social-card.jpg"><meta property="og:image:alt" content="APIZIT API launch illustration">' +
            '<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="' + escape(title) + '"><meta name="twitter:description" content="' + escape(page.summary) + '"><meta name="twitter:image" content="' + ORIGIN + BASE + 'assets/social-card.jpg">' +
            '<script src="' + BASE + 'assets/bootstrap.js"></script><script src="' + BASE + 'assets/docs.js" defer></script>' +
            '<script type="application/ld+json">' + JSON.stringify(structuredData(page,docs.catalog,ORIGIN+BASE),null,2).replaceAll("<","\\u003c") + '</script></head>' +
            '<body data-search-index="' + BASE + 'search-index.json"><a class="skip-link" href="#main-content">Skip to content</a>' +
            '<header class="site-header"><a class="brand" href="' + BASE + '">APIZIT Linking</a><nav aria-label="Primary"><a href="' + BASE + 'quickstart/">Quickstart</a><a href="' + BASE + 'guides/">Guides</a><a href="' + BASE + 'limits/#choose">Fit and limits</a><a href="https://github.com/chipsi44/apizit-linking-examples">GitHub</a></nav><button type="button" data-theme-toggle hidden>Switch to night mode</button></header>' +
            '<div class="docs-layout"><aside class="docs-navigation"><div class="cli-search" hidden><label for="cli-search">Search APIZIT Linking</label><input id="cli-search" type="search" autocomplete="off" aria-controls="cli-results"><p id="cli-search-status" role="status"></p><ul id="cli-results"></ul></div><details class="cli-menu" open><summary>Documentation menu</summary><nav aria-label="Documentation">' + navigation(docs.pages,BASE,page.slug) + '</nav></details></aside>' +
            '<main id="main-content" tabindex="-1"><nav aria-label="Breadcrumb"><a href="' + BASE + '">APIZIT Linking</a>' + (page.slug === "index" ? "" : " / " + escape(page.title)) + '</nav><p class="eyebrow">Version 0.5.0 · Public beta · Apache-2.0</p><article>' + page.html + '</article><p><a href="' + page.markdownUrl + '" download>Download this page as Markdown</a></p>' +
            '<footer><a href="' + BASE + 'releases/">Releases</a> · <a href="' + BASE + 'migrations/">Migrations</a> · <a href="' + BASE + 'security/">Security</a> · <a href="' + BASE + 'catalog.json">Page catalogue</a> · <a href="' + BASE + 'llms.txt">Agent index</a></footer></main>' +
            '<aside class="docs-toc"><nav aria-label="On this page"><strong>On this page</strong>' + page.headings.map(h=>'<a href="#'+h.id+'">'+escape(h.title)+'</a>').join("") + '</nav></aside></div><p id="cli-copy-status" role="status" class="visually-hidden"></p></body></html>\n';
        const directory=path.join(output,pagePath(page.slug));fs.mkdirSync(directory,{recursive:true});fs.writeFileSync(path.join(directory,"index.html"),html);
    }
    const urls=docs.pages.map(p=>ORIGIN+p.url);
    fs.writeFileSync(path.join(output,"sitemap.xml"),'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+urls.map(url=>"<url><loc>"+url+"</loc></url>").join("\n")+"\n</urlset>\n");
    fs.writeFileSync(path.join(output,"robots.txt"),"User-agent: *\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nSitemap: "+ORIGIN+BASE+"sitemap.xml\n");
    fs.writeFileSync(path.join(output,".nojekyll"),"");
    fs.writeFileSync(path.join(output,"404.html"),'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Page not found — APIZIT Linking</title><meta name="robots" content="noindex, follow"></head><body><main id="main-content"><h1>Page not found</h1><a href="'+BASE+'">Return to APIZIT Linking</a></main></body></html>');
    console.log("Built " + docs.pages.length + " documentation pages.");
    return output;
}
if(require.main===module) buildDocs();
module.exports={buildDocs};
