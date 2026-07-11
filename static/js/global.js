const handleDropdownClick = (e, elem_id) => {
    e.preventDefault();

    const dropDown = document.querySelector(`#${elem_id}`);
    dropDown.classList.toggle("hidden");
};

const handleShareClick = async (e, doc_id) => {
    e.preventDefault()

    if (!doc_id || !doc_id.trim() || doc_id.trim().length === 0) {
        alert("Document ID is not given!")
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(doc_id)
        alert("Document ID copied to clipboard ✅.\nShare this ID to let others join the document.")
    } else {
        alert("Copy failed, Clipboard API not available")
    }
};