import React, { useState, useEffect } from 'react';

export default function TodaysTodo() {
    const [todos, setTodos] = useState([]);
    const [newTodo, setNewTodo] = useState("");

    useEffect(() => {
        const saved = localStorage.getItem("planner_daily_todos");
        if (saved) setTodos(JSON.parse(saved));
    }, []);

    useEffect(() => {
        localStorage.setItem("planner_daily_todos", JSON.stringify(todos));
    }, [todos]);

    const addTodo = (e) => {
        e.preventDefault();
        if (!newTodo.trim()) return;
        setTodos([...todos, { id: Date.now(), text: newTodo, done: false }]);
        setNewTodo("");
    };

    const toggleTodo = (id) => {
        setTodos(todos.map(t => t.id === id ? { ...t, done: !t.done } : t));
    };

    const deleteTodo = (id) => {
        setTodos(todos.filter(t => t.id !== id));
    };

    return (
        <div className="bg-white rounded-lg shadow-sm border h-full flex flex-col">
            <div className="p-3 border-b bg-gray-50 font-semibold text-gray-700 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 11 12 14 22 4"></polyline><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
                Today's Focus
            </div>

            <div className="flex-1 overflow-y-auto p-2">
                {todos.length === 0 && <div className="text-center text-gray-400 text-xs mt-4">No daily goals set.</div>}
                <ul className="space-y-1">
                    {todos.map(t => (
                        <li key={t.id} className="group flex items-center gap-2 p-2 hover:bg-gray-50 rounded transition-colors">
                            <input
                                type="checkbox"
                                checked={t.done}
                                onChange={() => toggleTodo(t.id)}
                                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                            />
                            <span className={`flex-1 text-sm ${t.done ? 'line-through text-gray-400' : 'text-gray-700'}`}>{t.text}</span>
                            <button onClick={() => deleteTodo(t.id)} className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-all">×</button>
                        </li>
                    ))}
                </ul>
            </div>

            <form onSubmit={addTodo} className="p-2 border-t">
                <input
                    className="w-full border rounded px-2 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                    placeholder="+ Add goal..."
                    value={newTodo}
                    onChange={e => setNewTodo(e.target.value)}
                />
            </form>
        </div>
    );
}
