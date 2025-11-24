import React, { useEffect, useState } from "react";

// Weekly Planner React component
// Updated to use API for persistence

const WEEK_START_HOUR = 9;
const WEEK_END_HOUR = 18;
const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function uid() {
    return Math.random().toString(36).slice(2, 9);
}

function isoDate(d) {
    return d.toISOString().slice(0, 10);
}

function minutesToHM(mins) {
    const h = Math.floor(mins / 60);
    const m = mins % 60;
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

function toIcalDateTime(dt) {
    return dt.toISOString().replace(/[-:]/g, "").split(".")[0] + "Z";
}

function defaultWeekStart() {
    const now = new Date();
    const day = now.getDay();
    const diffToMonday = ((day + 6) % 7);
    const monday = new Date(now);
    monday.setDate(now.getDate() - diffToMonday);
    monday.setHours(0, 0, 0, 0);
    return monday;
}

function scheduleTasksIntoWeek(tasks, weekStartDate) {
    // tasks: array of {id, task_name, duration_minutes, priority, deadline (YYYY-MM-DD|null)}
    // Note: Backend uses 'task_name', frontend used 'name'. We need to map.

    const PR = { high: 0, medium: 1, low: 2 };
    const parseDate = (s) => (s ? new Date(s + "T00:00:00") : null);

    const tasksSorted = [...tasks].sort((a, b) => {
        const da = parseDate(a.deadline);
        const db = parseDate(b.deadline);
        if (da && db) {
            if (da - db !== 0) return da - db;
        } else if (da && !db) return -1;
        else if (!da && db) return 1;

        // Default priority to medium if missing
        const pA = a.priority ? a.priority.toLowerCase() : 'medium';
        const pB = b.priority ? b.priority.toLowerCase() : 'medium';

        if ((PR[pA] || 1) - (PR[pB] || 1) !== 0)
            return (PR[pA] || 1) - (PR[pB] || 1);

        return (Number(a.duration_minutes) || 60) - (Number(b.duration_minutes) || 60);
    });

    const slots = [];
    for (let i = 0; i < 7; i++) {
        const dayStart = new Date(weekStartDate);
        dayStart.setDate(weekStartDate.getDate() + i);
        dayStart.setHours(WEEK_START_HOUR, 0, 0, 0);
        const dayEnd = new Date(weekStartDate);
        dayEnd.setDate(weekStartDate.getDate() + i);
        dayEnd.setHours(WEEK_END_HOUR, 0, 0, 0);
        slots.push({ start: dayStart, end: dayEnd });
    }

    const events = [];
    for (const t of tasksSorted) {
        const dur = Number(t.duration_minutes) || 60;
        let placed = false;
        for (const s of slots) {
            const avail = (s.end - s.start) / 60000;
            if (avail >= dur) {
                const evStart = new Date(s.start);
                const evEnd = new Date(evStart.getTime() + dur * 60000);
                events.push({
                    id: uid(),
                    taskId: t.id,
                    start: evStart,
                    end: evEnd,
                    summary: t.task_name || t.name, // Handle both keys
                    priority: t.priority
                });
                s.start = new Date(evEnd);
                placed = true;
                break;
            }
        }
        if (!placed) {
            const lastDay = new Date(slots[6].end);
            const evStart = new Date(lastDay);
            const evEnd = new Date(evStart.getTime() + dur * 60000);
            events.push({
                id: uid(),
                taskId: t.id,
                start: evStart,
                end: evEnd,
                summary: t.task_name || t.name,
                priority: t.priority
            });
        }
    }
    return events;
}

function buildIcs(events) {
    const lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//manas-weekly-planner//EN"];
    for (const e of events) {
        lines.push("BEGIN:VEVENT");
        lines.push(`UID:${e.id}`);
        lines.push(`DTSTAMP:${toIcalDateTime(new Date())}`);
        lines.push(`DTSTART:${toIcalDateTime(e.start)}`);
        lines.push(`DTEND:${toIcalDateTime(e.end)}`);
        lines.push(`SUMMARY:${e.summary}`);
        lines.push("END:VEVENT");
    }
    lines.push("END:VCALENDAR");
    return lines.join("\r\n");
}

export default function WeeklyPlanner({ refreshTrigger }) {
    const [weekStart, setWeekStart] = useState(defaultWeekStart());
    const [tasks, setTasks] = useState([]);
    const [events, setEvents] = useState([]);
    const [showAdd, setShowAdd] = useState(false);
    const [form, setForm] = useState({ name: "", duration_minutes: 60, priority: "medium", deadline: "" });
    const [selectedEvent, setSelectedEvent] = useState(null);

    // Fetch tasks from API
    const fetchTasks = async () => {
        try {
            const res = await fetch('/api/tasks');
            const data = await res.json();
            setTasks(data);
        } catch (e) {
            console.error("Failed to fetch tasks", e);
        }
    };

    useEffect(() => {
        fetchTasks();
    }, [refreshTrigger]); // Re-fetch when trigger changes

    // Save tasks to API
    const saveTasksToApi = async (newTasks) => {
        try {
            await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newTasks)
            });
            setTasks(newTasks);
        } catch (e) {
            console.error("Failed to save tasks", e);
        }
    };

    useEffect(() => {
        const ev = scheduleTasksIntoWeek(tasks, weekStart);
        setEvents(ev);
    }, [tasks, weekStart]);

    function addTaskFromForm() {
        const newTask = {
            id: uid(),
            task_name: form.name || "Untitled", // Backend expects task_name
            duration_minutes: Number(form.duration_minutes) || 60,
            priority: form.priority || "medium",
            deadline: form.deadline || null,
            created_at: new Date().toISOString()
        };
        const newTasks = [...tasks, newTask];
        saveTasksToApi(newTasks);
        setForm({ name: "", duration_minutes: 60, priority: "medium", deadline: "" });
        setShowAdd(false);
    }

    function deleteTaskById(taskId) {
        const newTasks = tasks.filter((t) => t.id !== taskId);
        saveTasksToApi(newTasks);
    }

    function prevWeek() {
        const d = new Date(weekStart);
        d.setDate(d.getDate() - 7);
        setWeekStart(d);
    }
    function nextWeek() {
        const d = new Date(weekStart);
        d.setDate(d.getDate() + 7);
        setWeekStart(d);
    }

    function exportIcs() {
        const ics = buildIcs(events);
        const blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `weekly_schedule_${isoDate(weekStart)}.ics`;
        a.click();
        URL.revokeObjectURL(url);
    }

    function openEditEvent(ev) {
        setSelectedEvent(ev);
    }

    function saveEventEdits(edited) {
        const taskIdx = tasks.findIndex((t) => t.id === edited.taskId);
        if (taskIdx !== -1) {
            const t = { ...tasks[taskIdx] };
            t.earliest_start = edited.start.toISOString();
            const newDur = Math.round((edited.end - edited.start) / 60000);
            t.duration_minutes = newDur;
            const newTasks = [...tasks];
            newTasks[taskIdx] = t;
            saveTasksToApi(newTasks);
            setSelectedEvent(null);
        }
    }

    function renderGrid() {
        const hours = [];
        for (let h = WEEK_START_HOUR; h < WEEK_END_HOUR; h++) hours.push(h);

        return (
            <div className="w-full overflow-auto bg-white rounded-lg shadow-sm border h-full flex flex-col">
                <div className="flex items-center gap-2 p-4 border-b flex-shrink-0">
                    <button className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors" onClick={prevWeek}>Prev</button>
                    <div className="font-semibold text-lg">Week of {isoDate(weekStart)}</div>
                    <button className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded text-sm font-medium transition-colors" onClick={nextWeek}>Next</button>
                    <div className="ml-auto flex gap-2">
                        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium shadow-sm transition-colors" onClick={() => setShowAdd(true)}>+ Add Task</button>
                        <button className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium shadow-sm transition-colors" onClick={exportIcs}>Export .ics</button>
                    </div>
                </div>

                <div className="flex-1 overflow-auto">
                    <div className="grid grid-cols-8 gap-0 min-w-[800px]">
                        <div className="border-r border-b p-2 bg-gray-50 text-xs text-gray-500 font-medium uppercase tracking-wider text-center py-3 sticky top-0 z-20">Time</div>
                        {DAYS.map((d, i) => (
                            <div key={d} className="border-r border-b p-2 text-center bg-white sticky top-0 z-20 shadow-sm">
                                <div className="text-sm font-semibold text-gray-900">{d}</div>
                                <div className="text-xs text-gray-500 mt-1">{isoDate(new Date(weekStart).setDate(weekStart.getDate() + i)).slice(5)}</div>
                            </div>
                        ))}

                        {hours.map((h) => (
                            <React.Fragment key={h}>
                                <div className="border-r border-b p-2 text-xs text-gray-500 bg-gray-50 text-right pr-3 -mt-2.5">{String(h).padStart(2, '0')}:00</div>
                                {DAYS.map((d, i) => (
                                    <div key={d + h} className="border-r border-b min-h-[60px] relative group hover:bg-gray-50 transition-colors">
                                        {events.filter(ev => {
                                            const dayIndex = Math.floor((ev.start - weekStart) / (24 * 60 * 60 * 1000));
                                            return dayIndex === i && ev.start.getHours() === h;
                                        }).map(ev => (
                                            <div key={ev.id}
                                                className={`absolute left-1 right-1 top-1 rounded p-2 text-xs shadow-sm border cursor-pointer transition-all hover:shadow-md hover:scale-[1.02] z-10
                            ${ev.priority === 'high' ? 'bg-red-100 border-red-200 text-red-800' : ev.priority === 'medium' ? 'bg-blue-100 border-blue-200 text-blue-800' : 'bg-green-100 border-green-200 text-green-800'}`}
                                                onClick={() => openEditEvent(ev)}>
                                                <div className="font-semibold truncate">{ev.summary}</div>
                                                <div className="text-[10px] opacity-80">{minutesToHM((ev.end - ev.start) / 60000)}m</div>
                                            </div>
                                        ))}
                                    </div>
                                ))}
                            </React.Fragment>
                        ))}
                    </div>
                </div>

                {/* tasks list */}
                <div className="p-4 border-t bg-gray-50 max-h-60 overflow-y-auto flex-shrink-0">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-800">All Tasks</h3>
                        <div className="text-xs text-gray-500">Manage your backlog here</div>
                    </div>
                    <div className="grid gap-2">
                        {tasks.map(t => (
                            <div key={t.id} className="p-3 bg-white border rounded-md shadow-sm flex justify-between items-center hover:shadow-md transition-shadow">
                                <div>
                                    <div className="font-medium text-gray-900">{t.task_name || t.name}</div>
                                    <div className="text-xs text-gray-500 mt-0.5 flex items-center gap-2">
                                        <span className="bg-gray-100 px-1.5 py-0.5 rounded text-gray-600">{t.duration_minutes}m</span>
                                        <span className={`px-1.5 py-0.5 rounded capitalize ${t.priority === 'high' ? 'bg-red-100 text-red-700' : t.priority === 'medium' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'}`}>{t.priority}</span>
                                        {t.deadline && <span className="text-gray-400">Due {t.deadline}</span>}
                                    </div>
                                </div>
                                <div className="flex gap-2 items-center opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button className="px-2 py-1 bg-red-50 hover:bg-red-100 text-red-600 rounded text-xs transition-colors" onClick={() => deleteTaskById(t.id)}>Delete</button>
                                </div>
                            </div>
                        ))}
                        {tasks.length === 0 && <div className="text-center text-gray-400 text-sm py-4">No tasks yet. Add one to get started!</div>}
                    </div>
                </div>

                {/* add modal */}
                {showAdd && (
                    <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
                        <div className="bg-white p-6 rounded-lg shadow-xl w-[420px] animate-in fade-in zoom-in duration-200">
                            <h4 className="font-bold text-lg mb-4 text-gray-800">Add New Task</h4>
                            <div className="grid gap-4">
                                <div>
                                    <label className="block text-xs font-medium text-gray-700 mb-1">Task Name</label>
                                    <input className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all" placeholder="e.g., Study Physics" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} autoFocus />
                                </div>
                                <div className="flex gap-4">
                                    <div className="w-1/2">
                                        <label className="block text-xs font-medium text-gray-700 mb-1">Duration (min)</label>
                                        <input className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 outline-none" type="number" min={10} step={5} value={form.duration_minutes} onChange={e => setForm({ ...form, duration_minutes: e.target.value })} />
                                    </div>
                                    <div className="w-1/2">
                                        <label className="block text-xs font-medium text-gray-700 mb-1">Priority</label>
                                        <select className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 outline-none bg-white" value={form.priority} onChange={e => setForm({ ...form, priority: e.target.value })}>
                                            <option value="high">High</option>
                                            <option value="medium">Medium</option>
                                            <option value="low">Low</option>
                                        </select>
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-xs font-medium text-gray-700 mb-1">Deadline (Optional)</label>
                                    <input className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 outline-none" type="date" value={form.deadline} onChange={e => setForm({ ...form, deadline: e.target.value })} />
                                </div>
                                <div className="flex justify-end gap-3 mt-2">
                                    <button className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md text-sm font-medium transition-colors" onClick={() => setShowAdd(false)}>Cancel</button>
                                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium shadow-sm transition-colors" onClick={addTaskFromForm}>Add Task</button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* edit modal */}
                {selectedEvent && (
                    <EditEventModal event={selectedEvent} onClose={() => setSelectedEvent(null)} onSave={saveEventEdits} />
                )}

            </div>
        );
    }

    return (
        <div className="h-full flex flex-col">
            {renderGrid()}
        </div>
    );
}

function EditEventModal({ event, onClose, onSave }) {
    const [startStr, setStartStr] = useState(new Date(event.start).toISOString().slice(0, 16));
    const [endStr, setEndStr] = useState(new Date(event.end).toISOString().slice(0, 16));
    const [summary, setSummary] = useState(event.summary);

    function handleSave() {
        const s = new Date(startStr);
        const e = new Date(endStr);
        if (e <= s) {
            alert("End must be after start");
            return;
        }
        onSave({ id: event.id, taskId: event.taskId, summary, start: s, end: e });
    }

    return (
        <div className="fixed inset-0 flex items-center justify-center bg-black/50 backdrop-blur-sm z-50">
            <div className="bg-white p-6 rounded-lg shadow-xl w-[420px] animate-in fade-in zoom-in duration-200">
                <h4 className="font-bold text-lg mb-4 text-gray-800">Edit Event</h4>
                <div className="grid gap-4">
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Task Name</label>
                        <input className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 outline-none" value={summary} onChange={e => setSummary(e.target.value)} />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">Start Time</label>
                        <input className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 outline-none" type="datetime-local" value={startStr} onChange={e => setStartStr(e.target.value)} />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1">End Time</label>
                        <input className="w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-blue-500 outline-none" type="datetime-local" value={endStr} onChange={e => setEndStr(e.target.value)} />
                    </div>
                    <div className="flex justify-end gap-3 mt-2">
                        <button onClick={onClose} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md text-sm font-medium transition-colors">Cancel</button>
                        <button onClick={handleSave} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium shadow-sm transition-colors">Save Changes</button>
                    </div>
                </div>
            </div>
        </div>
    );
}
