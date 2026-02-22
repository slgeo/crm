import React from "react";
import FullCalendar from "@fullcalendar/react";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import resourceTimeGridPlugin from "@fullcalendar/resource-timegrid";
import ruLocale from "@fullcalendar/core/locales/ru";

export default function CalendarView({
  masters,
  appointments,
  handleDateClick,
  deleteAppointment
}) {
  return ( 
    <FullCalendar
      plugins={[
        interactionPlugin,
        timeGridPlugin,
        resourceTimeGridPlugin
      ]}
      locale={ruLocale}

      initialView="resourceTimeGridDay"

      // 🔥 15 минут
      slotDuration="00:15:00"
      slotLabelInterval="00:15:00"

      // 🔥 рабочие часы
      slotMinTime="08:00:00"
      slotMaxTime="22:00:00"

      // 🔥 автоскролл к текущему времени
      scrollTime={new Date().toISOString().slice(11, 19)}

      // 🔥 подсветка текущего времени
      nowIndicator={true}

      // 🔥 более компактный вид
      slotMinWidth={120}
      expandRows={true}
      height="auto"

      firstDay={1}

      headerToolbar={{
        left: "prev,next",
        center: "title",
        right: ""
      }}

      slotLabelFormat={{
        hour: "2-digit",
        minute: "2-digit",
        hour12: false
      }}

      eventTimeFormat={{
        hour: "2-digit",
        minute: "2-digit",
        hour12: false 
      }}

      resources={masters.map(m => ({
        id: m.id,
        title: m.name
      }))}

resourceLabelContent={(arg) => {
  const master = masters.find(m => m.id === Number(arg.resource.id));

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <img
        src={master?.avatar}
        alt=""
        style={{
          width: 28,
          height: 28,
          borderRadius: "50%",
          objectFit: "cover",
          border: `2px solid ${master?.color || "#6366f1"}`
        }}
      />
      <span>{arg.resource.title}</span>
    </div>
  );
}}
      events={appointments.map(a => {
        const master = masters.find(m => m.id === a.master_id);

        return {
          id: a.id,
          title: a.title,
          start: a.appointment_time,
          resourceId: a.master_id,
          backgroundColor: master?.color,
          borderColor: master?.color
        };
      })}
      dateClick={handleDateClick}
      eventClick={deleteAppointment}
    />
  );
}
