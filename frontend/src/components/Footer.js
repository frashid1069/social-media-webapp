import React from "react";
import "../loginStyles.css";

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
