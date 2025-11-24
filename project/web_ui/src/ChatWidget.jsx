import React, { useState, useRef, useEffect } from 'react';

export default function ChatWidget({ onTaskUpdate }) {
    const [messages, setMessages] = useState([
        { role: 'assistant', text: 'Hello! I can help you manage your tasks. Try "Add a high priority task to study".' }
    ]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const sendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input;
        setInput("");
        setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
        setLoading(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg })
            });
            const data = await res.json();

            setMessages(prev => [...prev, { role: 'assistant', text: data.response }]);

            // If the action was something that modifies tasks, trigger a refresh
            if (['add_task', 'delete_task', 'update_task', 'reschedule_task'].includes(data.action)) {
                if (onTaskUpdate) onTaskUpdate();
            }

        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', text: "Error connecting to server." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border h-full flex flex-col">
            <div className="p-3 border-b bg-gray-50 font-semibold text-gray-700 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                AI Assistant
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-3">
                {messages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-lg p-2 text-sm ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                            {m.text}
                        </div>
                    </div>
                ))}
                {loading && <div className="text-xs text-gray-400 ml-2">Thinking...</div>}
                <div ref={messagesEndRef} />
            </div>

            <form onSubmit={sendMessage} className="p-2 border-t flex gap-2">
                <input
                    className="flex-1 border rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="Ask me anything..."
                    value={input}
                    onChange={e => setInput(e.target.value)}
                />
                <button type="submit" disabled={loading} className="bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700 disabled:opacity-50">
                    Send
                </button>
            </form>
        </div>
    );
}
