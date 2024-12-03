import React from "react";
/**
 * This is a component for displaying the footer
 *
 *
 */
export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <p className="footer-text">
        © {currentYear} 404Web, All rights reserved.
      </p>
    </footer>
  );
}
