document.addEventListener('DOMContentLoaded', function() {
    const urlField = document.querySelector('#id_url');
    const nameField = document.querySelector('#id_name');
    const spinner = document.querySelector('.spinner');
    const favicon = document.querySelector('.favicon-preview');
    const searchInput = document.getElementById('search-input');
    const totalLinksElement = document.getElementById('total-links');
    const collectionList = document.getElementById('collection-list');
    const skeletonLoader = document.getElementById('skeleton-loader');

    let page = 1;
    let isLoading = false;
    let searchQuery = '';

    async function fetchMetadata(url) {
        try {
            const response = await fetch(`/collections/fetch_metadata/?url=${encodeURIComponent(url)}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (response.ok) {
                return await response.json();
            } else {
                console.error('Error fetching metadata');
                return null;
            }
        } catch (error) {
            console.error('Error during metadata fetch:', error);
            return null;
        }
    }

    async function updateMetadata() {
        const url = urlField.value.trim();
        nameField.value = '';
        favicon.style.display = 'none';
        if (url) {
            spinner.style.display = 'inline-block';
            const metadata = await fetchMetadata(url);
            spinner.style.display = 'none';
            if (metadata && !metadata.error) {
                favicon.src = metadata.favicon;
                favicon.style.display = 'inline-block';
                if (metadata.title) {
                    nameField.value = metadata.title;
                }
            } else {
                console.error('Failed to fetch metadata:', metadata ? metadata.error : 'Unknown error');
            }
        }
    }

    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    const debouncedUpdateMetadata = debounce(updateMetadata, 300);

    if (urlField) {
        urlField.addEventListener('input', debouncedUpdateMetadata);
        urlField.addEventListener('paste', function(e) {
            nameField.value = '';
            setTimeout(() => {
                updateMetadata();
            }, 0);
        });
    }

    function confirmDelete(collectionId) {
        var modal = document.getElementById('delete-confirmation-modal');
        if (!modal) {
            console.error("Delete confirmation modal not found!");
            return;
        }
    
        modal.style.display = 'flex';
    
        document.getElementById('confirm-yes').onclick = function() {
            window.location.href = `/collections/delete/${collectionId}/`;
        };
    
        document.getElementById('confirm-no').onclick = closeModal;
    }
    
    function closeModal() {
        var modal = document.getElementById('delete-confirmation-modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    function confirmDeleteLink(linkId) {
        var modal = document.getElementById('delete-link-confirmation-modal');
        if (!modal) {
            console.error("Delete link confirmation modal not found!");
            return;
        }
    
        modal.style.display = 'flex';
    
        document.getElementById('confirm-delete-link-yes').onclick = function() {
            deleteLink(linkId);
        };
    
        document.getElementById('confirm-delete-link-no').onclick = closeLinkModal;
    }
    
    function closeLinkModal() {
        var linkModal = document.getElementById('delete-link-confirmation-modal');
        if (linkModal) {
            linkModal.style.display = 'none';
        }
    }
    
    function deleteLink(linkId) {
        fetch(`/collections/delete_link/${linkId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
        }).then(response => {
            if (response.ok) {
                const linkCard = document.querySelector(`.collection-block[data-link-id="${linkId}"]`);
                if (linkCard) {
                    linkCard.remove();
                    updateTotalLinks(parseInt(totalLinksElement.textContent.split(':')[1].trim()) - 1);
                } else {
                    console.error('Link card not found in the DOM');
                }
                closeLinkModal();
            } else {
                console.error('Failed to delete link');
                alert('Failed to delete link. Please try again.');
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the link. Please try again.');
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function openAllLinks(collectionId) {
        if (collectionId) {
            // This is called from the collections list
            fetch(`/collections/get_collection_links/${collectionId}/`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                data.links.forEach(url => {
                    window.open(url, '_blank');
                });
            })
            .catch(error => {
                console.error('Error opening links:', error);
                alert('An error occurred while trying to open the links. Please try again.');
            });
        } else {
            // This is called from the collection details page
            const links = document.querySelectorAll('.collection-block a.btn-primary');
            links.forEach(link => {
                const url = link.getAttribute('href');
                window.open(url, '_blank');
            });
        }
    }
    
    function updateTotalLinks(total) {
        if (totalLinksElement) {
            totalLinksElement.textContent = `Total links: ${total}`;
        }
    }

    function loadMoreLinks(reset = false) {
        if (isLoading) return;
        isLoading = true;
        if (reset) {
            page = 1;
            collectionList.innerHTML = '';
        }
        skeletonLoader.style.display = 'block';
        document.getElementById('loading').style.display = 'none';
        const url = new URL(window.location.href);
        url.searchParams.set('page', page);
        url.searchParams.set('search', searchQuery);
        fetch(url, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        }).then(response => response.json()).then(data => {
            skeletonLoader.style.display = 'none';
            if (data.links.length === 0) {
                if (page === 1) {
                    collectionList.innerHTML = '<p>No links in this collection yet. Add one!</p>';
                }
                window.removeEventListener('scroll', handleScroll);
            } else {
                if (page === 1) {
                    collectionList.innerHTML = ''; // Clear the list before adding new links
                }
                data.links.forEach(link => {
                    const linkBlock = document.createElement('div');
                    linkBlock.classList.add('collection-block');
                    linkBlock.setAttribute('data-link-id', link.id);
                    linkBlock.innerHTML = `
                        <div class="collection-header">
                            <img src="${link.favicon_url}" alt="${link.name} Favicon" class="favicon" onerror="this.onerror=null; this.src='/static/main/img/default-favicon.svg'">
                            <h3>${link.name}</h3>
                        </div>
                        <p>${link.description}</p>
                        <div class="collection-buttons">
                            <a href="${link.url}" class="btn-primary" target="_blank">Visit link</a>
                            <button class="btn-secondary" onclick="copyToClipboard('${link.url}')">Copy</button>
                            <button class="btn-delete" onclick="confirmDeleteLink('${link.id}')">Delete</button>
                        </div>
                    `;
                    collectionList.appendChild(linkBlock);
                });
                if (data.has_next) {
                    page += 1;
                    document.getElementById('loading').style.display = 'block';
                } else {
                    window.removeEventListener('scroll', handleScroll);
                }
            }
            isLoading = false;
            updateTotalLinks(data.total_links);
        }).catch(error => {
            console.error('Error loading links:', error);
            skeletonLoader.style.display = 'none';
            if (page === 1) {
                collectionList.innerHTML = '<p>An error occurred while loading links</p>';
            } else {
                collectionList.innerHTML += '<p>An error occurred while loading more links</p>';
            }
            document.getElementById('loading').style.display = 'none';
            isLoading = false;
        });
    }


    function handleScroll() {
        const scrollPosition = window.innerHeight + window.scrollY;
        const threshold = document.body.offsetHeight - 100;
        if (scrollPosition >= threshold) {
            loadMoreLinks();
        }
    }

    function handleSearch() {
        searchQuery = searchInput.value.trim();
        loadMoreLinks(true);
    }

    const debouncedSearch = debounce(handleSearch, 300);

    if (searchInput) {
        searchInput.addEventListener('input', debouncedSearch);
    }

    window.addEventListener('scroll', handleScroll);

    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            alert('Link copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            alert('Failed to copy link. Please try again.');
        });
    }

    // Make these functions global so they can be called from inline event handlers
    window.confirmDelete = confirmDelete;
    window.closeModal = closeModal;
    window.confirmDeleteLink = confirmDeleteLink;
    window.closeLinkModal = closeLinkModal;
    window.openAllLinks = openAllLinks;
    window.copyToClipboard = copyToClipboard;

 // Initial load
// document.getElementById('initial-loading').style.display = 'flex';
skeletonLoader.style.display = 'block';
loadMoreLinks();
});

let lastScroll = 0;
let headerTimeout;
const header = document.getElementById('header');

window.addEventListener('scroll', () => {
    clearTimeout(headerTimeout);

    const currentScroll = window.pageYOffset;

    if (currentScroll < lastScroll) {
        header.classList.remove('header-hidden');
    }

    if (currentScroll > lastScroll) {
        headerTimeout = setTimeout(() => {
            if (currentScroll > 100) {
                header.classList.add('header-hidden');
            }
        }, 200);
    }

    if (currentScroll > 50) {
        header.classList.add('scrolled');
    } else {
        header.classList.remove('scrolled');
    }

    lastScroll = currentScroll;
});

document.addEventListener('mousemove', (e) => {
    if (e.clientY <= 100) {
        header.classList.remove('header-hidden');
    }
});