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

function wirePaperButtons() {
  const papers = document.querySelectorAll('.paper')
  for (const paper of papers) {
    const content = paper.querySelector('.paper-content')
    const nextButton = paper.querySelector('.paper-next')
    if (!content || !nextButton) continue

    const updateButton = () => {
      const pageEls = Array.from(paper.querySelectorAll('.paper-page'))
      if (pageEls.length <= 1) {
        nextButton.disabled = true
        nextButton.style.display = 'none'
        return
      }
      const maxScroll = content.scrollWidth - content.clientWidth
      nextButton.disabled = content.scrollLeft >= maxScroll - 2
      nextButton.style.display = ''
    }

    nextButton.addEventListener('click', () => {
      const pageEls = Array.from(paper.querySelectorAll('.paper-page'))
      if (!pageEls.length) return

      const currentLeft = content.scrollLeft
      const pageWidth = pageEls[0].offsetWidth

      // scroll la urmatoarea pagina
      const nextPageLeft = Math.ceil(currentLeft / pageWidth) * pageWidth + pageWidth
      const maxScroll = content.scrollWidth - content.clientWidth
      const targetLeft = Math.min(nextPageLeft, maxScroll)

      content.scrollTo({ left: targetLeft, behavior: 'smooth' })
    })

    content.addEventListener('scroll', updateButton, { passive: true })
    updateButton()
  }
}

function paginatePodcards() {
  const contents = document.querySelectorAll('.paper-content')
  for (const paperContent of contents) paginatePaperContent(paperContent)
  wirePaperButtons()
}

let resizeTimer = null
window.addEventListener('resize', () => {
  window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(() => paginatePodcards(), 150)
})

window.addEventListener('load', () => paginatePodcards())
