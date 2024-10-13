import React, { useState, useEffect } from "react";
import "../loginStyles.css";

export default function Stream({ author }) {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    // ......
  }, []);
  return (
    <div>
      <p>this is stream page</p>
    </div>
  );
}
