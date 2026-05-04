---
layout: page
permalink: /gallery/
title: gallery
description: Photography from my travels and city walks.
nav: true
nav_order: 4.5
_styles: >
  .gallery-page {
    margin-top: 1.5rem;
  }

  .gallery-toolbar {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
  }

  .gallery-profile-link {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    color: var(--global-text-color-light);
    font-size: 0.9rem;
    font-weight: 500;
  }

  .gallery-profile-link:hover {
    color: var(--global-theme-color);
    text-decoration: none;
  }

  .gallery-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.55rem;
  }

  .gallery-item {
    position: relative;
    display: block;
    width: 100%;
    aspect-ratio: 1;
    overflow: hidden;
    background: var(--global-card-bg-color);
    border: 0;
    border-radius: 6px;
    box-shadow: 0 0 0 1px var(--global-divider-color);
    cursor: zoom-in;
    padding: 0;
  }

  .gallery-item img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
    transition:
      transform 180ms ease,
      filter 180ms ease;
  }

  .gallery-item:hover img,
  .gallery-item:focus-visible img {
    transform: scale(1.035);
    filter: brightness(0.74);
  }

  .gallery-caption {
    position: absolute;
    inset: auto 0 0;
    padding: 2.5rem 0.75rem 0.7rem;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.68), rgba(0, 0, 0, 0));
    color: #fff;
    opacity: 0;
    transform: translateY(0.4rem);
    transition:
      opacity 180ms ease,
      transform 180ms ease;
  }

  .gallery-viewer {
    position: fixed;
    inset: 0;
    z-index: 1050;
    display: none;
    align-items: stretch;
    justify-content: center;
    background: rgba(12, 12, 12, 0.92);
  }

  .gallery-viewer.is-open {
    display: flex;
  }

  .gallery-viewer-open {
    overflow: hidden;
  }

  .gallery-viewer-shell {
    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(260px, 340px);
    width: min(1180px, 100%);
    min-height: 100%;
    background: var(--global-bg-color);
  }

  .gallery-viewer-media {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100%;
    padding: 2rem;
    background: #050505;
  }

  .gallery-viewer-media img {
    max-width: 100%;
    max-height: calc(100vh - 4rem);
    width: auto;
    height: auto;
    object-fit: contain;
  }

  .gallery-viewer-info {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 1.4rem;
    border-left: 1px solid var(--global-divider-color);
  }

  .gallery-viewer-info h2 {
    margin-bottom: 0.35rem;
    font-size: 1.15rem;
  }

  .gallery-viewer-info p {
    margin-bottom: 0;
    color: var(--global-text-color-light);
    font-size: 0.9rem;
  }

  .gallery-viewer-description {
    margin-top: 0.55rem;
    line-height: 1.55;
  }

  .gallery-viewer-meta {
    margin-top: 0.85rem;
    font-size: 0.82rem;
  }

  .gallery-viewer-description:empty,
  .gallery-viewer-meta:empty {
    display: none;
  }

  .gallery-viewer-source {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    margin-top: 1.25rem;
    color: var(--global-theme-color);
    font-size: 0.9rem;
    font-weight: 500;
  }

  .gallery-viewer-source[hidden] {
    display: none;
  }

  .gallery-viewer-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
    z-index: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    border: 0;
    border-radius: 999px;
    color: var(--global-text-color);
    background: var(--global-bg-color);
    box-shadow: 0 0 0 1px var(--global-divider-color);
    cursor: pointer;
  }

  .gallery-item:hover .gallery-caption,
  .gallery-item:focus-visible .gallery-caption {
    opacity: 1;
    transform: translateY(0);
  }

  .gallery-caption strong,
  .gallery-caption span {
    display: block;
    color: #fff;
  }

  .gallery-caption strong {
    font-size: 0.92rem;
    line-height: 1.2;
  }

  .gallery-caption span {
    margin-top: 0.2rem;
    font-size: 0.75rem;
    opacity: 0.84;
  }

  .gallery-empty {
    padding: 2rem 0;
    color: var(--global-text-color-light);
  }

  @media (max-width: 640px) {
    .gallery-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 0.45rem;
    }
  }

  @media (max-width: 760px) {
    .gallery-viewer-shell {
      grid-template-columns: 1fr;
      grid-template-rows: minmax(0, 1fr) auto;
    }

    .gallery-viewer-media {
      min-height: 0;
      padding: 3.8rem 1rem 1rem;
    }

    .gallery-viewer-media img {
      max-height: calc(100vh - 13rem);
    }

    .gallery-viewer-info {
      border-top: 1px solid var(--global-divider-color);
      border-left: 0;
    }
  }

  @media (max-width: 420px) {
    .gallery-grid {
      grid-template-columns: 1fr;
    }
  }
---

<div class="gallery-page">
  <div class="gallery-toolbar">
    <a class="gallery-profile-link" href="https://unsplash.com/@darth_u" target="_blank" rel="external nofollow noopener">
      <i class="fa-brands fa-unsplash"></i>
      <span>Unsplash</span>
    </a>
  </div>

{% if site.data.gallery and site.data.gallery.size > 0 %}

    <div class="gallery-grid" id="gallery">
      {% for photo in site.data.gallery %}
        {% if photo.thumb contains '://' %}
          {% assign thumb_src = photo.thumb %}
        {% else %}
          {% assign thumb_src = photo.thumb | relative_url %}
        {% endif %}
        {% if photo.full contains '://' %}
          {% assign full_src = photo.full %}
        {% else %}
          {% assign full_src = photo.full | relative_url %}
        {% endif %}
        {% capture photo_meta %}
          {% if photo.location %}{{ photo.location }}{% endif -%}
          {%- if photo.location and photo.year %} / {% endif -%}
          {%- if photo.year %}{{ photo.year }}{% endif %}
        {% endcapture %}
        <button
          class="gallery-item"
          type="button"
          data-full="{{ full_src }}"
          data-title="{{ photo.title | escape }}"
          data-alt="{{ photo.alt | default: photo.title | escape }}"
          data-description="{{ photo.description | default: photo.alt | default: photo.title | escape }}"
          data-meta="{{ photo_meta | strip | escape }}"
          data-source="{{ photo.source_url }}"
          aria-label="Open {{ photo.title }}"
        >
          <img
            src="{{ thumb_src }}"
            alt="{{ photo.alt | default: photo.title }}"
            width="640"
            height="640"
            loading="{% if forloop.index <= 6 %}eager{% else %}lazy{% endif %}"
            decoding="async"
            {% if forloop.index <= 3 %}
              fetchpriority="high"
            {% endif %}
          >
          <span class="gallery-caption">
            <strong>{{ photo.title }}</strong>
            {% if photo.location or photo.year %}
              <span>{{ photo_meta | strip }}</span>
            {% endif %}
          </span>
        </button>
      {% endfor %}
    </div>

{% else %}

<p class="gallery-empty">No photos selected.</p>
{% endif %}

</div>

<div class="gallery-viewer" id="gallery-viewer" aria-hidden="true">
  <div class="gallery-viewer-shell" role="dialog" aria-modal="true" aria-label="Photo viewer">
    <button class="gallery-viewer-close" type="button" aria-label="Close photo viewer" data-gallery-close>
      <i class="fa-solid fa-xmark"></i>
    </button>
    <div class="gallery-viewer-media">
      <img id="gallery-viewer-image" alt="">
    </div>
    <div class="gallery-viewer-info">
      <div>
        <h2 id="gallery-viewer-title"></h2>
        <p id="gallery-viewer-description" class="gallery-viewer-description"></p>
        <p id="gallery-viewer-meta" class="gallery-viewer-meta"></p>
      </div>
      <a id="gallery-viewer-source" class="gallery-viewer-source" href="https://unsplash.com/@darth_u" target="_blank" rel="external nofollow noopener">
        <i class="fa-brands fa-unsplash"></i>
        <span>View on Unsplash</span>
      </a>
    </div>
  </div>
</div>

<script>
  (() => {
    const viewer = document.getElementById("gallery-viewer");
    if (!viewer) return;

    const image = document.getElementById("gallery-viewer-image");
    const title = document.getElementById("gallery-viewer-title");
    const description = document.getElementById("gallery-viewer-description");
    const meta = document.getElementById("gallery-viewer-meta");
    const source = document.getElementById("gallery-viewer-source");
    const closeButton = viewer.querySelector("[data-gallery-close]");
    let lastFocus = null;

    const openViewer = (trigger) => {
      lastFocus = trigger;
      image.src = trigger.dataset.full;
      image.alt = trigger.dataset.alt || trigger.dataset.title || "";
      title.textContent = trigger.dataset.title || "";
      description.textContent = trigger.dataset.description || "";
      meta.textContent = trigger.dataset.meta || "";
      if (trigger.dataset.source) {
        source.href = trigger.dataset.source;
        source.hidden = false;
      } else {
        source.hidden = true;
      }
      viewer.classList.add("is-open");
      viewer.setAttribute("aria-hidden", "false");
      document.documentElement.classList.add("gallery-viewer-open");
      closeButton.focus();
    };

    const closeViewer = () => {
      viewer.classList.remove("is-open");
      viewer.setAttribute("aria-hidden", "true");
      document.documentElement.classList.remove("gallery-viewer-open");
      image.removeAttribute("src");
      if (lastFocus) lastFocus.focus();
    };

    document.querySelectorAll(".gallery-item").forEach((item) => {
      item.addEventListener("click", () => openViewer(item));
    });

    closeButton.addEventListener("click", closeViewer);
    viewer.addEventListener("click", (event) => {
      if (event.target === viewer) closeViewer();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && viewer.classList.contains("is-open")) closeViewer();
    });
  })();
</script>
