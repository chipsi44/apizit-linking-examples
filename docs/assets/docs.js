(() => {
    const toggle=document.querySelector("[data-theme-toggle]");
    function updateTheme(){toggle.textContent=document.documentElement.dataset.theme==="dark"?"Switch to day mode":"Switch to night mode";toggle.setAttribute("aria-pressed",String(document.documentElement.dataset.theme==="dark"));}
    if(toggle){toggle.hidden=false;updateTheme();toggle.addEventListener("click",()=>{const next=document.documentElement.dataset.theme==="dark"?"light":"dark";document.documentElement.dataset.theme=next;try{localStorage.setItem("apizit.linking.theme",next);}catch(_){}updateTheme();});}
    const menu=document.querySelector(".cli-menu");if(menu&&matchMedia("(max-width:800px)").matches)menu.open=false;
    for(const button of document.querySelectorAll("[data-copy-code]")) {
        if(!navigator.clipboard?.writeText)continue;
        button.hidden=false;
        button.addEventListener("click",async()=>{const status=document.getElementById("cli-copy-status");try{await navigator.clipboard.writeText(document.getElementById(button.dataset.copyCode).textContent);status.textContent="Example copied.";button.textContent="Copied";}catch(_){status.textContent="Clipboard unavailable. Select and copy the example manually.";}});
    }
    const input=document.getElementById("cli-search");if(!input)return;
    const results=document.getElementById("cli-results"),status=document.getElementById("cli-search-status");
    let index=null;
    document.querySelector(".cli-search").hidden=false;
    input.addEventListener("input",async()=>{
        const term=input.value.trim().toLowerCase();
        if(!term){results.replaceChildren();status.textContent="";return;}
        try {
            if(!index)index=await fetch(document.body.dataset.searchIndex).then(r=>{if(!r.ok)throw new Error("Search unavailable");return r.json();});
            if(input.value.trim().toLowerCase()!==term)return;
            const matches=index.filter(p=>(p.title+" "+p.text).toLowerCase().includes(term)).slice(0,12);
            results.replaceChildren();
            for(const item of matches){if(!item.url.startsWith("/apizit-linking-examples/")||item.url.includes("\\"))continue;const li=document.createElement("li"),a=document.createElement("a");a.href=item.url;a.textContent=item.title;li.append(a);results.append(li);}
            status.textContent=matches.length?matches.length+" results":"No matching topics.";
        } catch(_){status.textContent="Search unavailable. Use the documentation menu.";}
    });
})();
