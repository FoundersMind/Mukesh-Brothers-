// -*- coding: utf-8 -*-
// Handle Bottom Navigation on Scroll



let lastScrollY = window.scrollY;
const bottomNav = document.querySelector(".bottom-nav");

if (bottomNav) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > lastScrollY) {
            bottomNav.classList.add("hidden"); // Hide on scroll down
        } else {
            bottomNav.classList.remove("hidden"); // Show on scroll up
        }
        lastScrollY = window.scrollY;
    });
}


// Navbar Toggle Button
const navbarToggler = document.querySelector(".navbar-toggler");
const secondNavItems = document.querySelector(".navbar-collapse");

if (navbarToggler && secondNavItems) {
    navbarToggler.addEventListener("click", function () {
        secondNavItems.classList.toggle("show");
    });

    // Close when clicking outside
    document.addEventListener("click", function (event) {
        if (!secondNavItems.contains(event.target) && !navbarToggler.contains(event.target)) {
            secondNavItems.classList.remove("show");
        }
    });
}

// Toggle Login Text
const loginLink = document.getElementById("login-link");
if (loginLink) {
    loginLink.addEventListener("click", function () {
        loginLink.textContent = loginLink.textContent === "Login" ? "Welcome" : "Login";
    });
}

// Profile Dropdown Toggle
const profileDropdown = document.getElementById("profileDropdown");
if (profileDropdown) {
    profileDropdown.addEventListener("click", function (event) {
        event.preventDefault();
        const dropdownMenu = this.nextElementSibling;
        if (dropdownMenu) {
            dropdownMenu.classList.toggle("show");
        }
    });
}

// Close Profile Dropdown when Clicking Outside
document.addEventListener("click", function (event) {
    const profileDropdown = document.getElementById("profileDropdown");
    const dropdownMenu = document.getElementById("profileDropdownMenu");

    if (profileDropdown && dropdownMenu) {
        if (!profileDropdown.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove("show");
        }
    }
});

// Logout Functionality
const logoutLink = document.getElementById("logoutLink");
if (logoutLink) {
    logoutLink.addEventListener("click", function (event) {
        event.preventDefault();
        window.location.href = "/logout";
    });
}

// Update Login Link Href
if (profileDropdown) {
    profileDropdown.addEventListener("click", function () {
        const loginLink = document.getElementById("loginLink");
        if (loginLink && this.innerHTML.includes("Login")) {
            loginLink.href = "/Login";
        }
    });
}

// Product Dropdown
const dropdownMenuButton = document.getElementById("dropdownMenuButton");
const dropdownMenu = document.querySelector(".product-dropdown-menu");

if (dropdownMenuButton && dropdownMenu) {
    dropdownMenuButton.addEventListener("click", function () {
        dropdownMenu.classList.toggle("show");
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (event) {
        if (!dropdownMenu.contains(event.target) && !dropdownMenuButton.contains(event.target)) {
            dropdownMenu.classList.remove("show");
        }
    });
}
