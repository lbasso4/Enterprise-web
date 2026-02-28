function buscar2() {
  // First, remove any previous highlights
  removeHighlights();

  const input = document.getElementById("searchInput").value.trim();

  if (input === "") {
    alert("Escriu alguna paraula per cercar.");
    return;
  }
  
  const searchableAreas = [
    document.querySelector(".impressores-wrapper"),
    document.querySelector(".noticies-wrapper"),
    document.querySelector(".hero-overlay")
  ];

  let totalMatches = 0;

  searchableAreas.forEach(area => {
    if (area) totalMatches += highlightText(area, input);
  });

  if (totalMatches === 0) {
    alert("No s'han trobat resultats per: " + input);
  } else {
    alert("S'han trobat " + totalMatches + " resultats per: " + input);
  }
}


function highlightText(node, searchTerm) {
  let count = 0;
  if (node.nodeType === Node.TEXT_NODE) {
    const index = node.textContent.toLowerCase().indexOf(searchTerm.toLowerCase());
    if (index !== -1) {
      const before = node.textContent.slice(0, index);
      const match = node.textContent.slice(index, index + searchTerm.length);
      const after = node.textContent.slice(index + searchTerm.length);

      // Create a <mark> element to wrap the matched word
      const mark = document.createElement("mark");
      mark.textContent = match;

      const fragment = document.createDocumentFragment();
      if (before) fragment.appendChild(document.createTextNode(before));
      fragment.appendChild(mark);
      if (after) fragment.appendChild(document.createTextNode(after));

      node.parentNode.replaceChild(fragment, node);
      count++;
    }
  } 
  // If it's an element node (like <p>, <h3>, etc.), go through its children
  else if (
    node.nodeType === Node.ELEMENT_NODE &&
    !["SCRIPT", "STYLE", "INPUT", "BUTTON", "TEXTAREA"].includes(node.nodeName)
  ) {
    // We use Array.from because the childNodes list changes as we modify it
    Array.from(node.childNodes).forEach(child => { count += highlightText(child, searchTerm);
    });
  }
return count;
}

function removeHighlights() {
  document.querySelectorAll("mark").forEach(mark => {
    mark.parentNode.replaceChild(document.createTextNode(mark.textContent), mark);
    mark.parentNode.normalize();
  });
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("searchInput").addEventListener("keydown", function (e) {
    if (e.key === "Enter") buscar2();
  });
});
