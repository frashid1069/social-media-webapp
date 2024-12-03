import React, { useState } from 'react';
import { cusFetch } from "./Login";

const ChatAssistant = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [speaking, setSpeaking] = useState(false);
    const apiUrl = process.env.REACT_APP_API_URL;

    const toggleChat = () => setIsOpen(!isOpen);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const newMessages = [...messages, { sender: 'user', text: input }];
        setMessages(newMessages);
        setInput('');

        try {
            const response = await cusFetch(`${apiUrl}chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: input }),
            });
            const data = await response.json();
            const botMessage = data.response;
            setMessages([...newMessages, { sender: 'bot', text: data.response }]);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    const readAloud = (text) => {
        const synth = window.speechSynthesis;

        if (speaking) {
            synth.cancel();
            setSpeaking(false);
            return;
        }

        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';

            // Update speaking state when speech starts and ends
            utterance.onstart = () => setSpeaking(true);
            utterance.onend = () => setSpeaking(false);

            synth.speak(utterance);
        } else {
            console.error('Speech synthesis is not supported in this browser.');
        }
    };

    return (
        <div id="chat-assistant">
            <button id="chat-toggle" onClick={toggleChat}>
                {isOpen ? (
                    <span className="close-icon">✖</span> // Close button
                ) : (
                    <img
                        src="/cute.png" // Replace with the actual path to your logo
                        alt="Open Chat"
                        className="chat-icon"
                    />
                )}
            </button>
            {isOpen && (
                <div id="chat-window">
                    <div id="chat-header">Chat with AI</div>
                    <div id="chat-messages">
                        {messages.map((msg, index) => (
                            <div key={index} className={`chat-message ${msg.sender}`}>
                                {msg.text}
                                {msg.sender === 'bot' && (
                                    <button
                                        className="read-aloud-btn"
                                        onClick={() => readAloud(msg.text)}
                                    >
                                        🔊 Read Aloud
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                    <div id="chat-input-container">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Type a message..."
                        />
                        <button onClick={sendMessage}>Send</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatAssistant;