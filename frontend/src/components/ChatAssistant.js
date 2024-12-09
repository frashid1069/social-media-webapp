import React, { useState, useEffect } from 'react';
import { cusFetch } from "./Login";
import { DynamicPlaceholder } from "./utils/WordAnimation"

const ChatAssistant = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [speaking, setSpeaking] = useState(false);
    const apiUrl = process.env.REACT_APP_API_URL;
    const dynamicPlaceholder = new DynamicPlaceholder('home-stock-input');

    const toggleChat = () => setIsOpen(!isOpen);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const newMessages = [...messages, { sender: 'user', text: input }];
        setMessages(newMessages);
        setInput('');

        try {
            const response = await cusFetch(`${apiUrl}chat/`, {
                method: 'POST',
                body: JSON.stringify({ prompt: input }),
            });
            const data = await response.json();
            const botMessage = data.response;
            setMessages([...newMessages, { sender: 'bot', text: data.response }]);
        } catch (error) {
            console.error('Error:', error);
        }
    };

    useEffect(() => {
        if (isOpen) {
            // Initialize DynamicPlaceholder when the chat is opened
            const dynamicPlaceholder = new DynamicPlaceholder("chat-input");
            dynamicPlaceholder.init();
        }
    }, [isOpen]);

    const readAloud = (text, buttonRef) => {
        const synth = window.speechSynthesis;

        if (speaking) {
            synth.cancel();
            setSpeaking(false);
            buttonRef.classList.remove('speaking');
            return;
        }
        
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'en-US';

            // Update speaking state when speech starts and ends
            utterance.onstart = () => {
                setSpeaking(true);
                buttonRef.classList.add('speaking');
            };
            utterance.onend = () => {
                setSpeaking(false);
                buttonRef.classList.remove('speaking');
            };

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
                        src={`${process.env.PUBLIC_URL}/cute.png`} // Replace with the actual path to your logo
                        alt="Open Chat"
                        className="chat-icon"
                    />
                )}
            </button>
            {isOpen && (
                <div id="chat-window">
                    <div id="chat-header">Chat with Aqua AI</div>
                    <div id="chat-messages">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`chat-message ${msg.sender}`}
                                style={{
                                    flexDirection: msg.sender === 'bot' ? 'row' : 'row-reverse',
                                    alignItems: 'center',
                                }}
                            >
                                <img
                                    src={msg.sender === 'bot'
                                        ? `${process.env.PUBLIC_URL}/chat-logo.jpg`
                                        : `${process.env.PUBLIC_URL}/login-image.png`}
                                    alt={`${msg.sender} logo`}
                                    className="chat-logo"
                                />
                                <span>{msg.text}</span>
                                {msg.sender === 'bot' && (
                                    <button
                                        className="read-aloud-btn"
                                        onClick={(e) => readAloud(msg.text, e.currentTarget)}
                                    >
                                        🔊 Read Aloud
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                    <div id="chat-input-container">
                        <input
                            id='chat-input'
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                        />
                        <button type="submit" onClick={sendMessage}>Send</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatAssistant;