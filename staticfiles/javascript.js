// -*- coding: utf-8 -*-
document.addEventListener('DOMContentLoaded', function() {
    // Your JavaScript code here
    
    const navbarToggler = document.querySelector(".navbar-toggler");
    const secondNavItems = document.querySelector(".navbar-collapse");

    if (navbarToggler && secondNavItems) {
        navbarToggler.addEventListener("click", function() {
            secondNavItems.classList.toggle("show");
        });

        // Close the toggle list when clicking outside of it
        document.addEventListener("click", function(event) {
            if (secondNavItems && !secondNavItems.contains(event.target) && !navbarToggler.contains(event.target)) {
                secondNavItems.classList.remove("show");
            }
        });
    }
    
    

    function toggleLogin() {
        var loginLink = document.getElementById("login-link");
        if (loginLink && loginLink.textContent == "Login") {
            loginLink.textContent = "Welcome";
        } else {
            loginLink.textContent = "Login";
        }
    }
   
    var profileDropdown = document.getElementById("profileDropdown");
    if (profileDropdown) {
        profileDropdown.addEventListener("click", function(event) {
            event.preventDefault();
            var dropdownMenu = this.nextElementSibling;
            if (dropdownMenu) {
                dropdownMenu.classList.toggle("show");
            }
        });
    }
  
    // Close the profile dropdown when clicking outside of it
    document.addEventListener("click", function(event) {
        var profileDropdown = document.getElementById("profileDropdown");
        var dropdownMenu = document.getElementById("profileDropdownMenu");
        var clickedElement = event.target;
        
        // Check if the clicked element is not the profile dropdown or its menu
        if (profileDropdown && dropdownMenu && !profileDropdown.contains(clickedElement) && !dropdownMenu.contains(clickedElement)) {
            dropdownMenu.classList.remove("show");
        }
    });
  
    var logoutLink = document.getElementById("logoutLink");
    if (logoutLink) {
        logoutLink.addEventListener("click", function(event) {
            event.preventDefault();
            // Perform logout action (e.g., redirect to logout URL)
            window.location.href = "/logout";
        });
    }
  
    // Update login link href when changing from "Profile" to "Login"
    var profileDropdown = document.getElementById("profileDropdown");
    if (profileDropdown) {
        profileDropdown.addEventListener("click", function(event) {
            if (this.innerHTML.includes("Login")) {
                document.getElementById("loginLink").href = "/Login";
            }
        });
    }
   var dropdownMenuButton = document.getElementById("dropdownMenuButton");
    var dropdownMenu = document.querySelector(".product-dropdown-menu");
    
    dropdownMenuButton.addEventListener("click", function() {
        
      dropdownMenu.classList.toggle("show");
      
     
    });
  
    document.addEventListener("click", function(event) {
      if (!dropdownMenu.contains(event.target) && !dropdownMenuButton.contains(event.target)) {
        dropdownMenu.classList.remove("show");
      }
    });
    // document.addEventListener('DOMContentLoaded', function() {
      
    });
    

    
