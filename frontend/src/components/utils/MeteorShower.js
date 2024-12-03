import React, { useEffect, useState } from "react";

const MeteorShower = ({ count = 6 }) => {
  const [meteors, setMeteors] = useState([]);

  useEffect(() => {
    const generateMeteors = () => {
      const newMeteors = Array.from({ length: count }).map(() => ({
        id: Math.random().toString(36).substr(2, 9), // Unique ID for each meteor
        top: -100 + Math.random() * 10, // Top position between 0% and 30%
        left: Math.random() * 300, // Left position between 70% and 100%
        duration: 3 + Math.random() * 5, // Duration between 3s and 5s
        delay: Math.random() * 3, // Delay up to 3s
      }));
      setMeteors(newMeteors);
    };

    generateMeteors();
  }, [count]);

  return (
    <div className="meteor-shower">
      {meteors.map((meteor) => (
        <div
          key={meteor.id}
          className="meteor"
          style={{
            top: `${meteor.top}vh`,
            left: `${meteor.left}vw`,
            animation: `meteorMove ${meteor.duration}s linear ${meteor.delay}s infinite`,
          }}
        />
      ))}
    </div>
  );
};

export default MeteorShower;
