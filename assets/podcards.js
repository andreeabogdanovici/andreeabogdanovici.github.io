function paginatePaperContent(paperContent) {
  const existingPages = paperContent.querySelector('.paper-pages')
  if (existingPages) existingPages.remove()

  const prose = paperContent.querySelector('.prose')
  if (!prose) return

  const sourceHtml = prose.getAttribute('data-source-html') || prose.innerHTML
  prose.setAttribute('data-source-html', sourceHtml)

  const pages = document.createElement('div')
  pages.className = 'paper-pages'
  prose.replaceWith(pages)

  const paperHeight = paperContent.clientHeight
  const createPage = () => {
    const el = document.createElement('div')
    el.className = 'paper-page prose'
    el.style.height = paperHeight + 'px'
    pages.appendChild(el)
    return el
  }

  let current = createPage()
  const scratch = document.createElement('div')
  scratch.innerHTML = sourceHtml
  const nodes = Array.from(scratch.childNodes)

  for (const node of nodes) {
    if (node.nodeType === Node.TEXT_NODE && !node.textContent.trim()) continue
    current.appendChild(node)
    if (current.scrollHeight > current.clientHeight) {
      current.removeChild(node)
      current = createPage()
      current.appendChild(node)
    }
  }
}

function paginatePodcards() {
  const contents = document.querySelectorAll('.paper-content')
  for (const paperContent of contents) paginatePaperContent(paperContent)
}

let resizeTimer = null
window.addEventListener('resize', () => {
  window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(() => paginatePodcards(), 150)
})

window.addEventListener('load', () => paginatePodcards())
