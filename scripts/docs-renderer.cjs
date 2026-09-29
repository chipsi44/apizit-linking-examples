const escape = (value) => String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[character]));
const anchor = (value) => value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
function inline(value) {
    let result = "";
    let offset = 0;
    const tokens = /`([^`]+)`|\[([^\]\n]+)\]\(([^\s)]+)\)|\*\*([^*]+)\*\*/g;
    for (const match of String(value).matchAll(tokens)) {
        result += escape(String(value).slice(offset, match.index));
        if (match[1] !== undefined) result += `<code>${escape(match[1])}</code>`;
        else if (match[2] !== undefined) {
            const href = match[3];
            if (!/^(?:https:\/\/[^\s\\]+|\/(?!\/)[^\s\\]*|#[A-Za-z0-9_-]+)$/.test(href)
                || /[\u0000-\u001f\u007f]/.test(href)) {
                throw new Error(`Unsafe documentation link: ${href}`);
            }
            result += `<a href="${escape(href)}">${escape(match[2])}</a>`;
        } else result += `<strong>${escape(match[4])}</strong>`;
        offset = match.index + match[0].length;
    }
    return result + escape(String(value).slice(offset));
}

function renderMarkdown(markdown) {
    const lines = markdown.replace(/\r/g, "").split("\n");
    const output = [];
    const headings = [];
    const ids = new Set();
    let index = 0;
    let codeIndex = 0;
    while (index < lines.length) {
        const line = lines[index];
        if (!line.trim()) { index += 1; continue; }
        const fence = line.match(/^```([a-z0-9]*)$/);
        if (fence) {
            const code = [];
            index += 1;
            while (index < lines.length && lines[index] !== "```") code.push(lines[index++]);
            if (index === lines.length) throw new Error("Unclosed customer documentation code block.");
            index += 1;
            codeIndex += 1;
            const label = ({powershell: "PowerShell", sh: "Shell", yaml: "YAML", json: "JSON", text: "Text", python: "Python", javascript: "JavaScript", typescript: "TypeScript", java: "Java", http: "HTTP"})[fence[1]] || "Code";
            output.push(`<figure class="cli-code"><figcaption><span>${label}</span><button type="button" data-copy-code="code-${codeIndex}" aria-label="Copy ${label} example ${codeIndex}" hidden>Copy</button></figcaption><pre tabindex="0" aria-label="${label} example ${codeIndex}"><code id="code-${codeIndex}">${escape(code.join("\n"))}</code></pre></figure>`);
            continue;
        }
        const explicitAnchor = line.match(/^<a id="([A-Za-z][A-Za-z0-9_-]*)"><\/a>$/);
        if (explicitAnchor) {
            if (ids.has(explicitAnchor[1])) throw new Error("Duplicate documentation anchor.");
            ids.add(explicitAnchor[1]);
            output.push(line);
            index += 1;
            continue;
        }
        const heading = line.match(/^(#{1,6}) (.+?)(?: \{#([A-Za-z][A-Za-z0-9_-]*)\})?$/);
        if (heading) {
            const level = heading[1].length;
            const title = heading[2].replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/[`*]/g, "");
            const id = heading[3] || anchor(title);
            if (output.at(-1) === `<a id="${id}"></a>`) {
                output.pop();
                ids.delete(id);
            }
            if (ids.has(id)) throw new Error(`Duplicate documentation heading: ${id}`);
            ids.add(id);
            if (level > 1) headings.push({id, title});
            output.push(`<h${level} id="${id}" aria-label="${escape(title)}">${inline(heading[2])}${level > 1 ? `<a class="cli-anchor" href="#${id}" aria-label="Link to ${escape(title)}">#</a>` : ""}</h${level}>`);
            index += 1;
            continue;
        }
        if (line.startsWith("|")) {
            const rows = [];
            while (index < lines.length && lines[index].startsWith("|")) {
                const row = lines[index++].replaceAll("\\|", "\u0001").split("|").slice(1, -1).map((part) => part.trim().replaceAll("\u0001", "|"));
                if (row.every((part) => /^:?-+:?$/.test(part))) continue;
                rows.push(row);
            }
            output.push(`<div class="cli-table-scroll" role="region" aria-label="Reference table" tabindex="0"><table><thead><tr>${rows[0].map((part) => `<th scope="col">${inline(part)}</th>`).join("")}</tr></thead><tbody>${rows.slice(1).map((row) => `<tr>${row.map((part) => `<td>${inline(part)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`);
            continue;
        }
        if (line.startsWith("- ") || /^\d+\. /.test(line)) {
            const ordered = /^\d+\. /.test(line);
            const pattern = ordered ? /^\d+\. / : /^- /;
            const items = [];
            while (index < lines.length && pattern.test(lines[index])) {
                const item = [lines[index++].replace(pattern, "")];
                while (index < lines.length && /^ {2}\S/.test(lines[index])) item.push(lines[index++].trim());
                items.push(`<li>${inline(item.join(" "))}</li>`);
            }
            const tag = ordered ? "ol" : "ul";
            output.push(`<${tag}>${items.join("")}</${tag}>`);
            continue;
        }
        const paragraph = [];
        while (index < lines.length && lines[index].trim() && !/^(#|```|\||- |\d+\. )/.test(lines[index])) paragraph.push(lines[index++]);
        if (!paragraph.length) throw new Error("Unsupported documentation syntax.");
        output.push(`<p>${inline(paragraph.join(" "))}</p>`);
    }
    return {html: output.join("\n"), headings};
}


module.exports = {renderMarkdown, escape, anchor};
