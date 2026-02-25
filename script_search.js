function buscar() {
  // First, remove any previous highlights
  removeHighlights();

  let input = document.getElementById("searchInput").value.trim();

  if (input === "") {
    alert("Escriu alguna paraula per cercar.");
    return;
  }

  // We'll search inside the body, but skip the search bar itself
  const body = document.body;
  highlightText(body, input);
}

function highlightText(node, searchTerm) {
  // If it's a text node, look for the search term inside it
  if (node.nodeType === Node.TEXT_NODE) {
    const index = node.textContent.toLowerCase().indexOf(searchTerm.toLowerCase());
    if (index !== -1) {
      // Split the text into 3 parts: before, match, after
      const before = node.textContent.slice(0, index);
      const match = node.textContent.slice(index, index + searchTerm.length);
      const after = node.textContent.slice(index + searchTerm.length);

      // Create a <mark> element to wrap the matched word
      const mark = document.createElement("mark");
      mark.textContent = match;

      // Replace the original text node with the 3 parts
      const fragment = document.createDocumentFragment();
      if (before) fragment.appendChild(document.createTextNode(before));
      fragment.appendChild(mark);
      if (after) fragment.appendChild(document.createTextNode(after));

      node.parentNode.replaceChild(fragment, node);
    }
  } 
  // If it's an element node (like <p>, <h3>, etc.), go through its children
  else if (
    node.nodeType === Node.ELEMENT_NODE &&
    node.nodeName !== "SCRIPT" &&
    node.nodeName !== "STYLE" &&
    node.nodeName !== "INPUT" &&
    node.nodeName !== "BUTTON"
  ) {
    // We use Array.from because the childNodes list changes as we modify it
    Array.from(node.childNodes).forEach(child => highlightText(child, searchTerm));
  }
}

function removeHighlights() {
  // Find all <mark> elements and replace them with plain text
  document.querySelectorAll("mark").forEach(mark => {
    const parent = mark.parentNode;
    parent.replaceChild(document.createTextNode(mark.textContent), mark);
    // Merge split text nodes back together
    parent.normalize();
  });
}
