try {
    const saved=localStorage.getItem("apizit.linking.theme");
    if(saved==="dark"||saved==="light") document.documentElement.dataset.theme=saved;
} catch (_) { /* The documentation works without browser storage. */ }
