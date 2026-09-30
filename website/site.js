"use strict";

const search = document.querySelector("#gallery-search");
if (search) {
  const cards = [...document.querySelectorAll(".figure-card")];
  const buttons = [...document.querySelectorAll("[data-filter]")];
  let selected = "All";
  const update = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    cards.forEach(card => {
      const match = (selected === "All" || card.dataset.category === selected) &&
        card.dataset.search.toLocaleLowerCase().includes(query);
      card.hidden = !match;
      if (match) count++;
    });
    document.querySelector("#result-count").textContent = `${count} ${count === 1 ? "example" : "examples"}`;
    document.querySelector("#gallery-empty").hidden = count !== 0;
    buttons.forEach(button => {
      const active = button.dataset.filter === selected;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
  };
  buttons.forEach(button => button.addEventListener("click", () => {
    selected = button.dataset.filter;
    update();
  }));
  search.addEventListener("input", update);
  document.querySelector("#clear-filters").addEventListener("click", () => {
    selected = "All";
    search.value = "";
    update();
    search.focus();
  });
}

const dialog = document.querySelector("#figure-viewer");
if (dialog && typeof dialog.showModal === "function") {
  let trigger;
  const viewerImage = dialog.querySelector("img");
  document.querySelectorAll("a.image-zoom").forEach(link => link.addEventListener("click", event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    trigger = link;
    viewerImage.src = link.href;
    viewerImage.alt = link.querySelector("img")?.alt || link.getAttribute("aria-label") || "Scientific figure";
    dialog.querySelector(".viewer-caption").textContent = viewerImage.alt;
    dialog.showModal();
  }));
  dialog.querySelector("button").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener("close", () => { if (trigger) trigger.focus(); });
}

document.querySelectorAll(".tutorial-content img").forEach(img => {
  if (img.closest("a")) return;
  const link = document.createElement("a");
  link.href = img.src;
  link.className = "tutorial-image-link";
  link.setAttribute("aria-label", `Open full-size image: ${img.alt}`);
  img.parentNode.insertBefore(link, img);
  link.appendChild(img);
});
