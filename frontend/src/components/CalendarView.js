import React from "react";
import FullCalendar from "@fullcalendar/react";
import interactionPlugin from "@fullcalendar/interaction";
import timeGridPlugin from "@fullcalendar/timegrid";
import resourceTimeGridPlugin from "@fullcalendar/resource-timegrid";
import ruLocale from "@fullcalendar/core/locales/ru";

export default function CalendarView({
  masters,
  appointments,
  services,
  clients,
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
      slotDuration="00:15:00"
      slotLabelInterval="00:15:00"
      slotMinTime="08:00:00"
      slotMaxTime="18:30:00"
      scrollTime={new Date().toISOString().slice(11, 19)}
      nowIndicator={true}
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
      resources={masters.map((m) => ({
        id: m.id,
        title: m.name
      }))}
      resourceLabelContent={(arg) => {
        const master = masters.find((m) => m.id === Number(arg.resource.id));

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
      events={appointments.map((appointment) => {
        const master = masters.find((m) => m.id === appointment.master_id);
        const service = services.find((s) => s.id === appointment.service_id);
        const client = clients.find((c) => c.id === appointment.client_id);

        const startDate = new Date(appointment.appointment_time);
        const durationMinutes = service?.duration_minutes || 60;
        const endDate = new Date(startDate.getTime() + durationMinutes * 60 * 1000);

        return {
          id: appointment.id,
          title: appointment.title,
          start: appointment.appointment_time,
          end: endDate.toISOString(),
          resourceId: appointment.master_id,
          backgroundColor: master?.color,
          borderColor: master?.color,
          extendedProps: {
            clientName: client?.name || "",
            clientPhone: client?.phone || ""
          }
        };
      })}
      eventContent={(arg) => {
        const clientName = arg.event.extendedProps.clientName;
        const clientPhone = arg.event.extendedProps.clientPhone;

        return (
          <div style={{ fontSize: 12, lineHeight: 1.25 }}>
            <div style={{ fontWeight: 600 }}>{arg.timeText} {arg.event.title}</div>
            {clientName && <div>👤 {clientName}</div>}
            {clientPhone && <div>📞 {clientPhone}</div>}
          </div>
        );
      }}
      dateClick={handleDateClick}
      eventClick={deleteAppointment}
    />
  );
}
