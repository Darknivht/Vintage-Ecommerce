/**
 * VINTAGE MODERN - NIGERIAN MARKETPLACE
 * Advanced JavaScript Framework
 * ===================================
 */

class VintageModern {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.handleLoading();
        this.initializeAnimations();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            this.initMobileMenu();
            this.initBackToTop();
            this.initCategoryDropdown();
            this.initSearch();
            this.initCart();
            this.initWishlist();
            this.initCounters();
            this.initTooltips();
        });

        window.addEventListener('scroll', () => {
            this.handleScroll();
        });

        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    initializeComponents() {
        // Initialize all interactive components
        this.initProductCards();
        this.initFilters();
        this.initPagination();
        this.initModals();
    }

    handleLoading() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    loadingScreen.classList.add('fade-out');
                    setTimeout(() => {
                        loadingScreen.style.display = 'none';
                    }, 500);
                }, 1000);
            });
        }
    }

    initializeAnimations() {
        // Initialize AOS if available
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-in-out',
                once: true,
                offset: 100
            });
        }
    }

    // Mobile Menu Management
    initMobileMenu() {
        const mobileToggle = document.getElementById('mobileMenuToggle');
        const mobileOverlay = document.getElementById('mobileMenuOverlay');
        const mobileClose = document.getElementById('mobileMenuClose');

        if (mobileToggle && mobileOverlay) {
            mobileToggle.addEventListener('click', () => {
                mobileOverlay.classList.add('active');
                mobileToggle.classList.add('active');
                document.body.style.overflow = 'hidden';
            });

            const closeMobileMenu = () => {
                mobileOverlay.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.style.overflow = '';
            };

            if (mobileClose) {
                mobileClose.addEventListener('click', closeMobileMenu);
            }

            mobileOverlay.addEventListener('click', (e) => {
                if (e.target === mobileOverlay) {
                    closeMobileMenu();
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && mobileOverlay.classList.contains('active')) {
                    closeMobileMenu();
                }
            });
        }
    }

    // Back to Top Button
    initBackToTop() {
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            backToTop.addEventListener('click', () => {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    }

    // Category Dropdown
    initCategoryDropdown() {
        const categoryBtn = document.getElementById('categoryBtn');
        const categoryMenu = document.getElementById('categoryMenu');

        if (categoryBtn && categoryMenu) {
            let timeout;

            categoryBtn.addEventListener('mouseenter', () => {
                clearTimeout(timeout);
                categoryMenu.style.display = 'block';
                setTimeout(() => {
                    categoryMenu.style.opacity = '1';
                    categoryMenu.style.visibility = 'visible';
                    categoryMenu.style.transform = 'translateY(0)';
                }, 10);
            });

            categoryBtn.addEventListener('mouseleave', () => {
                timeout = setTimeout(() => {
                    categoryMenu.style.opacity = '0';
                    categoryMenu.style.visibility = 'hidden';
                    categoryMenu.style.transform = 'translateY(-10px)';
                    setTimeout(() => {
                        categoryMenu.style.display = 'none';
                    }, 300);
                }, 100);
            });

            categoryMenu.addEventListener('mouseenter', () => {
                clearTimeout(timeout);
            });

            categoryMenu.addEventListener('mouseleave', () => {
                timeout = setTimeout(() => {
                    categoryMenu.style.opacity = '0';
                    categoryMenu.style.visibility = 'hidden';
                    categoryMenu.style.transform = 'translateY(-10px)';
                    setTimeout(() => {
                        categoryMenu.style.display = 'none';
                    }, 300);
                }, 100);
            });
        }
    }

    // Search Functionality
    initSearch() {
        const searchInput = document.querySelector('.search-input');
        const searchForm = document.querySelector('.search-form');

        if (searchInput) {
            // Add search suggestions (can be enhanced with AJAX)
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value;
                if (query.length > 2) {
                    this.showSearchSuggestions(query);
                } else {
                    this.hideSearchSuggestions();
                }
            });

            // Handle search form submission
            if (searchForm) {
                searchForm.addEventListener('submit', (e) => {
                    const query = searchInput.value.trim();
                    if (!query) {
                        e.preventDefault();
                        this.showNotification('Please enter a search term', 'warning');
                    }
                });
            }
        }
    }

    showSearchSuggestions(query) {
        // This can be enhanced with AJAX calls to get real suggestions
        console.log('Searching for:', query);
    }

    hideSearchSuggestions() {
        // Hide search suggestions dropdown
    }

    // Cart Management
    initCart() {
        // Add to cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.add-to-cart-btn') || e.target.closest('.add-to-cart-btn')) {
                e.preventDefault();
                const btn = e.target.matches('.add-to-cart-btn') ? e.target : e.target.closest('.add-to-cart-btn');
                const productId = btn.dataset.productId;
                this.addToCart(productId);
            }
        });

        // Cart quantity updates
        document.addEventListener('click', (e) => {
            if (e.target.matches('.cart-qty-plus')) {
                this.updateCartQuantity(e.target, 'increase');
            } else if (e.target.matches('.cart-qty-minus')) {
                this.updateCartQuantity(e.target, 'decrease');
            }
        });
    }

    addToCart(productId) {
        // Show loading state
        const btn = document.querySelector(`[data-product-id="${productId}"]`);
        if (btn) {
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Adding...';
            btn.disabled = true;

            // AJAX API call
            fetch('/ajax/add-to-cart/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.updateCartCount(data.cart_count);
                    this.showNotification('Product added to cart!', 'success');
                    
                    // Animate button
                    btn.innerHTML = '<i class="fas fa-check me-2"></i>Added!';
                    btn.classList.add('btn-success');
                    
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.classList.remove('btn-success');
                        btn.disabled = false;
                    }, 2000);
                } else {
                    this.showNotification(data.message || 'Error adding to cart', 'error');
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.showNotification('Error adding to cart', 'error');
                btn.innerHTML = originalText;
                btn.disabled = false;
            });
        }
    }

    updateCartQuantity(element, action) {
        const cartItem = element.closest('.cart-item');
        const qtyInput = cartItem.querySelector('.cart-qty-input');
        const currentQty = parseInt(qtyInput.value);
        
        let newQty = action === 'increase' ? currentQty + 1 : currentQty - 1;
        newQty = Math.max(1, newQty); // Minimum quantity is 1
        
        qtyInput.value = newQty;
        
        // Update cart via AJAX
        const productId = cartItem.dataset.productId;
        this.updateCartItem(productId, newQty);
    }

    updateCartItem(productId, quantity) {
        fetch('/ajax/update-cart/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateCartTotals(data);
            } else {
                this.showNotification(data.message || 'Error updating cart', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Error updating cart', 'error');
        });
    }

    updateCartCount(count) {
        const cartBadge = document.getElementById('cartCount');
        if (cartBadge) {
            cartBadge.textContent = count;
            cartBadge.classList.add('scale-in');
            setTimeout(() => {
                cartBadge.classList.remove('scale-in');
            }, 300);
        }
    }

    updateCartTotals(data) {
        // Update cart totals in the UI
        const subtotalEl = document.querySelector('.cart-subtotal');
        const totalEl = document.querySelector('.cart-total');
        
        if (subtotalEl) subtotalEl.textContent = data.subtotal;
        if (totalEl) totalEl.textContent = data.total;
    }

    // Wishlist Management
    initWishlist() {
        document.addEventListener('click', (e) => {
            if (e.target.matches('.wishlist-btn') || e.target.closest('.wishlist-btn')) {
                e.preventDefault();
                const btn = e.target.matches('.wishlist-btn') ? e.target : e.target.closest('.wishlist-btn');
                const productId = btn.dataset.productId;
                this.toggleWishlist(productId, btn);
            }
        });
    }

    toggleWishlist(productId, btn) {
        const icon = btn.querySelector('i');
        const isInWishlist = icon.classList.contains('fas');
        
        fetch('/customer/toggle-wishlist/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: JSON.stringify({
                product_id: productId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (data.added) {
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    btn.classList.add('text-danger');
                    this.showNotification('Added to wishlist!', 'success');
                } else {
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    btn.classList.remove('text-danger');
                    this.showNotification('Removed from wishlist!', 'info');
                }
                
                this.updateWishlistCount(data.wishlist_count);
            } else {
                this.showNotification(data.message || 'Error updating wishlist', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Error updating wishlist', 'error');
        });
    }

    updateWishlistCount(count) {
        const wishlistBadge = document.getElementById('wishlistCount');
        if (wishlistBadge) {
            wishlistBadge.textContent = count;
            wishlistBadge.classList.add('scale-in');
            setTimeout(() => {
                wishlistBadge.classList.remove('scale-in');
            }, 300);
        }
    }

    // Counter Animation
    initCounters() {
        const counters = document.querySelectorAll('.counter');
        const observerOptions = {
            threshold: 0.5,
            rootMargin: '0px 0px -100px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateCounter(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        counters.forEach(counter => {
            observer.observe(counter);
        });
    }

    animateCounter(element) {
        const target = parseInt(element.dataset.target);
        const duration = 2000; // 2 seconds
        const increment = target / (duration / 16); // 60fps
        let current = 0;

        const updateCounter = () => {
            current += increment;
            if (current < target) {
                element.textContent = Math.floor(current).toLocaleString();
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target.toLocaleString();
            }
        };

        updateCounter();
    }

    // Product Cards
    initProductCards() {
        const productCards = document.querySelectorAll('.product-card');
        
        productCards.forEach(card => {
            // Add hover effects
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-8px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    }

    // Filters
    initFilters() {
        const filterInputs = document.querySelectorAll('input[name="category"], input[name="brand"], input[name="rating"], input[name="availability"], input[name="price_range"]');
        
        filterInputs.forEach(input => {
            input.addEventListener('change', () => {
                setTimeout(() => {
                    this.applyFilters();
                }, 300);
            });
        });

        // Price range inputs
        const priceInputs = document.querySelectorAll('.price-input');
        priceInputs.forEach(input => {
            input.addEventListener('input', () => {
                clearTimeout(this.priceTimeout);
                this.priceTimeout = setTimeout(() => {
                    this.applyFilters();
                }, 1000);
            });
        });
    }

    applyFilters() {
        const form = document.createElement('form');
        form.method = 'GET';
        
        // Collect all filter values
        const filters = document.querySelectorAll('input[type="checkbox"]:checked, input[type="radio"]:checked, .price-input');
        
        filters.forEach(filter => {
            if (filter.value) {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = filter.name;
                input.value = filter.value;
                form.appendChild(input);
            }
        });
        
        // Preserve search query
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('q')) {
            const searchInput = document.createElement('input');
            searchInput.type = 'hidden';
            searchInput.name = 'q';
            searchInput.value = urlParams.get('q');
            form.appendChild(searchInput);
        }
        
        document.body.appendChild(form);
        form.submit();
    }

    // Pagination
    initPagination() {
        const paginationLinks = document.querySelectorAll('.pagination a');
        
        paginationLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const href = link.getAttribute('href');
                
                // Add loading state
                link.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                
                // Navigate to page
                window.location.href = href;
            });
        });
    }

    // Modals
    initModals() {
        // Quick view modal
        window.quickView = (productId) => {
            this.showQuickView(productId);
        };

        // Compare modal
        window.addToCompare = (productId) => {
            this.addToCompare(productId);
        };
    }

    showQuickView(productId) {
        // Create and show quick view modal
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Quick View</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="text-center">
                            <i class="fas fa-spinner fa-spin fa-2x"></i>
                            <p class="mt-2">Loading product details...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Load product data
        fetch(`/ajax/product-quick-view/${productId}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    modal.querySelector('.modal-body').innerHTML = data.html;
                } else {
                    modal.querySelector('.modal-body').innerHTML = '<p class="text-center text-danger">Error loading product details</p>';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                modal.querySelector('.modal-body').innerHTML = '<p class="text-center text-danger">Error loading product details</p>';
            });
        
        // Remove modal from DOM when hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }

    addToCompare(productId) {
        // Add product to comparison
        let compareList = JSON.parse(localStorage.getItem('compareList') || '[]');
        
        if (compareList.includes(productId)) {
            this.showNotification('Product already in comparison', 'warning');
            return;
        }
        
        if (compareList.length >= 4) {
            this.showNotification('You can compare maximum 4 products', 'warning');
            return;
        }
        
        compareList.push(productId);
        localStorage.setItem('compareList', JSON.stringify(compareList));
        
        this.showNotification('Product added to comparison', 'success');
        this.updateCompareCount(compareList.length);
    }

    updateCompareCount(count) {
        const compareBadge = document.getElementById('compareCount');
        if (compareBadge) {
            compareBadge.textContent = count;
            compareBadge.style.display = count > 0 ? 'block' : 'none';
        }
    }

    // Tooltips
    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Scroll Handler
    handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Back to top button
        const backToTop = document.getElementById('backToTop');
        if (backToTop) {
            if (scrollTop > 300) {
                backToTop.classList.add('show');
            } else {
                backToTop.classList.remove('show');
            }
        }
        
        // Navbar scroll effect
        const navbar = document.getElementById('mainNavbar');
        if (navbar) {
            if (scrollTop > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        }
    }

    // Resize Handler
    handleResize() {
        // Handle responsive changes
        const width = window.innerWidth;
        
        // Close mobile menu on resize to desktop
        if (width > 991) {
            const mobileOverlay = document.getElementById('mobileMenuOverlay');
            const mobileToggle = document.getElementById('mobileMenuToggle');
            
            if (mobileOverlay && mobileOverlay.classList.contains('active')) {
                mobileOverlay.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    }

    // Notification System
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.innerHTML = `
            <div class="alert-content">
                <i class="fas fa-${this.getNotificationIcon(type)} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.messages-container') || this.createMessagesContainer();
        container.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    createMessagesContainer() {
        const container = document.createElement('div');
        container.className = 'messages-container';
        document.body.appendChild(container);
        return container;
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Utility Functions
    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    formatCurrency(amount) {
        return new Intl.NumberFormat('en-NG', {
            style: 'currency',
            currency: 'NGN'
        }).format(amount);
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
}

// Initialize the application
const vintageApp = new VintageModern();

// Global functions for backward compatibility
window.addToCart = (productId) => vintageApp.addToCart(productId);
window.toggleWishlist = (productId, btn) => vintageApp.toggleWishlist(productId, btn);
window.quickView = (productId) => vintageApp.showQuickView(productId);
window.addToCompare = (productId) => vintageApp.addToCompare(productId);

// Make the app available globally as VintageMarketplace for template compatibility
window.VintageMarketplace = vintageApp;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VintageModern;
}