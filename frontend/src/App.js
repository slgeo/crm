import React, { useState, useEffect } from "react";
import axios from "axios";

import {
  Box, Drawer, AppBar, Toolbar, Typography,
  List, ListItem, ListItemButton, ListItemText,
  CssBaseline, Button, Grid, Card, CardContent,
  Paper, IconButton, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField,
  FormControl, InputLabel, Select, MenuItem,
  Avatar
} from "@mui/material";

import { createTheme, ThemeProvider } from "@mui/material/styles";

import MenuIcon from "@mui/icons-material/Menu";
import DashboardIcon from "@mui/icons-material/Dashboard";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import PeopleIcon from "@mui/icons-material/People";
import BarChartIcon from "@mui/icons-material/BarChart";
import DeleteIcon from "@mui/icons-material/Delete";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import BuildIcon from "@mui/icons-material/Build";
import BadgeIcon from "@mui/icons-material/Badge";
import CategoryIcon from "@mui/icons-material/Category";

import {
  BarChart, Bar, XAxis, YAxis,
  Tooltip, ResponsiveContainer
} from "recharts";

import CalendarView from "./components/CalendarView";

const drawerWidth = 240;

export default function App() {

  const [page, setPage] = useState("calendar");
  const [open, setOpen] = useState(true);
  const [referenceOpen, setReferenceOpen] = useState(false);

  const [appointments, setAppointments] = useState([]);
  const [masters, setMasters] = useState([]);

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const [masterDialogOpen, setMasterDialogOpen] = useState(false);
  const [editingMasterId, setEditingMasterId] = useState(null);

  const [newMaster, setNewMaster] = useState({
    name: "",
    phone: "",
    percent: 40,
    color: "#6366f1",
    avatar: ""
  });

  const [newEvent, setNewEvent] = useState({
    title: "",
    date: "",
    time: "09:00",
    price: "",
    master_id: ""
  });

  const theme = createTheme({
    palette: { mode: "light", primary: { main: "#6366f1" } }
  });

  // ---------------- LOAD ----------------

  const loadData = () => {
    axios.get("/api/appointments").then(r => setAppointments(r.data));
    axios.get("/api/masters").then(r => setMasters(r.data));
  };

  useEffect(() => { loadData(); }, []);

  // ---------------- KPI ----------------

  const totalRevenue = appointments.reduce(
    (s, a) => s + (a.price || 0), 0
  );

  // ---------------- MASTER CRUD ----------------

  const saveMaster = () => {

    if (editingMasterId) {
      axios.put(`/api/masters/${editingMasterId}`, newMaster)
        .then(() => {
          setMasterDialogOpen(false);
          setEditingMasterId(null);
          loadData();
        });
    } else {
      axios.post("/api/masters", newMaster)
        .then(() => {
          setMasterDialogOpen(false);
          loadData();
        });
    }

    setNewMaster({
      name: "",
      phone: "",
      percent: 40,
      color: "#6366f1",
      avatar: ""
    });
  };

  const deleteMaster = (id) => {
    axios.delete(`/api/masters/${id}`)
      .then(() => loadData());
  };

  // ---------------- EVENTS ----------------

  const handleDateClick = (info) => {
    const dateObj = new Date(info.date);
    const hours = String(dateObj.getHours()).padStart(2,"0");
    const minutes = String(dateObj.getMinutes()).padStart(2,"0");

    setEditingId(null);

    setNewEvent({
      title: "",
      date: info.dateStr.split("T")[0],
      time: `${hours}:${minutes}`,
      price: "",
      master_id: info.resource?.id || ""
    });

    setDialogOpen(true);
  };

  const handleEventClick = (info) => {
    const event = appointments.find(a => a.id === Number(info.event.id));
    if (!event) return;

    const dateObj = new Date(event.appointment_time);
    const hours = String(dateObj.getHours()).padStart(2,"0");
    const minutes = String(dateObj.getMinutes()).padStart(2,"0");

    setEditingId(event.id);

    setNewEvent({
      title: event.title,
      date: event.appointment_time.slice(0,10),
      time: `${hours}:${minutes}`,
      price: event.price,
      master_id: event.master_id
    });

    setDialogOpen(true);
  };

  const saveEvent = () => {

    const payload = {
      title: newEvent.title,
      price: parseFloat(newEvent.price) || 0,
      datetime: `${newEvent.date}T${newEvent.time}:00`,
      master_id: newEvent.master_id
    };

    if (editingId) {
      axios.put(`/api/appointments/${editingId}`, payload)
        .then(() => {
          setDialogOpen(false);
          setEditingId(null);
          loadData();
        });
    } else {
      axios.post("/api/appointments", payload)
        .then(() => {
          setDialogOpen(false);
          loadData();
        });
    }
  };

  const deleteAppointment = () => {
    axios.delete(`/api/appointments/${editingId}`)
      .then(() => {
        setDialogOpen(false);
        setEditingId(null);
        loadData();
      });
  };

  // ---------------- FINANCE ----------------

  const financeData = masters.map(m => {
    const masterAppointments = appointments.filter(
      a => a.master_id === m.id
    );
    return {
      name: m.name,
      revenue: masterAppointments.reduce(
        (s,a) => s + (a.price || 0), 0
      )
    };
  });

  return (
    <ThemeProvider theme={theme}>
      <Box sx={{ display:"flex" }}>
        <CssBaseline />

        <AppBar position="fixed" sx={{ zIndex:1201 }}>
          <Toolbar>
            <IconButton onClick={()=>setOpen(!open)} color="inherit">
              <MenuIcon/>
            </IconButton>
            <Typography sx={{ flexGrow:1, ml:2 }}>
              Salon CRM
            </Typography>
          </Toolbar>
        </AppBar>

        <Drawer
          variant="permanent"
          sx={{
            width: open ? drawerWidth : 72,
            [`& .MuiDrawer-paper`]: {
              width: open ? drawerWidth : 72
            }
          }}
        >
          <Toolbar/>

          <List>

            <ListItem disablePadding>
              <ListItemButton selected={page==="calendar"} onClick={()=>setPage("calendar")}>
                <CalendarMonthIcon sx={{ mr: open?2:"auto" }}/>
                {open && <ListItemText primary="Календарь"/>}
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton selected={page==="finance"} onClick={()=>setPage("finance")}>
                <BarChartIcon sx={{ mr: open?2:"auto" }}/>
                {open && <ListItemText primary="Финансы"/>}
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton selected={page==="dashboard"} onClick={()=>setPage("dashboard")}>
                <DashboardIcon sx={{ mr: open?2:"auto" }}/>
                {open && <ListItemText primary="Dashboard"/>}
              </ListItemButton>
            </ListItem>

            <ListItem disablePadding>
              <ListItemButton onClick={()=>setReferenceOpen(!referenceOpen)}>
                <MenuBookIcon sx={{ mr: open?2:"auto" }}/>
                {open && <ListItemText primary="Справочники"/>}
              </ListItemButton>
            </ListItem>

            {referenceOpen && (
              <>
		   	    <ListItem disablePadding sx={{ pl: open ? 4 : 1 }}>
				  <ListItemButton
					selected={page==="serviceCategories"}
					onClick={()=>setPage("serviceCategories")}
				  >
				<CategoryIcon sx={{ mr: open?2:"auto" }}/>
					{open && <ListItemText primary="Категории услуг"/>}
  			      </ListItemButton>
			    </ListItem>
				
                <ListItem disablePadding sx={{ pl: open ? 4 : 1 }}>
                  <ListItemButton selected={page==="services"} onClick={()=>setPage("services")}>
                    <BuildIcon sx={{ mr: open?2:"auto" }}/>
                    {open && <ListItemText primary="Услуги"/>}
                  </ListItemButton>
                </ListItem>

                <ListItem disablePadding sx={{ pl: open ? 4 : 1 }}>
                  <ListItemButton selected={page==="positions"} onClick={()=>setPage("positions")}>
                    <BadgeIcon sx={{ mr: open?2:"auto" }}/>
                    {open && <ListItemText primary="Должности"/>}
                  </ListItemButton>
                </ListItem>

                <ListItem disablePadding sx={{ pl: open ? 4 : 1 }}>
                  <ListItemButton selected={page==="masters"} onClick={()=>setPage("masters")}>
                    <PeopleIcon sx={{ mr: open?2:"auto" }}/>
                    {open && <ListItemText primary="Мастера"/>}
                  </ListItemButton>
                </ListItem>
              </>
            )}

          </List>
        </Drawer>

        <Box component="main" sx={{ flexGrow:1, p:4 }}>
          <Toolbar/>

          {page==="calendar" && (
            <Paper sx={{ p:3 }}>
              <CalendarView
                masters={masters}
                appointments={appointments}
                handleDateClick={handleDateClick}
                deleteAppointment={handleEventClick}
              />
            </Paper>
          )}

          {page==="finance" && (
            <Paper sx={{ p:3, height:400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={financeData}>
                  <XAxis dataKey="name"/>
                  <YAxis/>
                  <Tooltip/>
                  <Bar dataKey="revenue" fill="#6366f1"/>
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          )}

          {page==="dashboard" && (
            <Card>
              <CardContent>
                <Typography variant="h5">
                  Оборот: {totalRevenue} ₽
                </Typography>
              </CardContent>
            </Card>
          )}

		  {page==="serviceCategories" && (
		    <Typography variant="h5">Раздел "Категории услуг"</Typography>
		  )}
          
		  {page==="services" && (
            <Typography variant="h5">Раздел "Услуги"</Typography>
          )}

          {page==="positions" && (
            <Typography variant="h5">Раздел "Должности"</Typography>
          )}

          {page==="masters" && (
            <>
              <Button
                variant="contained"
                sx={{ mb:2 }}
                onClick={()=>{
                  setEditingMasterId(null);
                  setNewMaster({
                    name:"",
                    phone:"",
                    percent:40,
                    color:"#6366f1",
                    avatar:""
                  });
                  setMasterDialogOpen(true);
                }}
              >
                Добавить мастера
              </Button>

              <Grid container spacing={3}>
                {masters.map(m=>(
                  <Grid item xs={12} md={4} key={m.id}>
                    <Card
                      sx={{ cursor:"pointer" }}
                      onClick={()=>{
                        setEditingMasterId(m.id);
                        setNewMaster({
                          name: m.name || "",
                          phone: m.phone || "",
                          percent: m.percent || 40,
                          color: m.color || "#6366f1",
                          avatar: m.avatar || ""
                        });
                        setMasterDialogOpen(true);
                      }}
                    >
                      <CardContent sx={{ display:"flex", alignItems:"center", gap:2 }}>
                        <Avatar
                          src={m.avatar}
                          sx={{ bgcolor:m.color, width:56, height:56 }}
                        >
                          {m.name?.[0]}
                        </Avatar>

                        <Box sx={{ flexGrow:1 }}>
                          <Typography variant="h6">{m.name}</Typography>
                          <Typography variant="body2">{m.phone}</Typography>
                          <Typography variant="body2">
                            {m.percent}%
                          </Typography>
                        </Box>

                        <IconButton
                          onClick={(e)=>{
                            e.stopPropagation();
                            deleteMaster(m.id);
                          }}
                        >
                          <DeleteIcon/>
                        </IconButton>

                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </>
          )}

        </Box>

        {/* EVENT DIALOG */}
        <Dialog open={dialogOpen} onClose={()=>setDialogOpen(false)}>
          <DialogTitle>
            {editingId ? "Редактирование записи" : "Новая запись"}
          </DialogTitle>

          <DialogContent>
            <TextField fullWidth margin="dense" label="Название"
              value={newEvent.title}
              onChange={(e)=>setNewEvent({...newEvent,title:e.target.value})}
            />

            <TextField fullWidth margin="dense" type="time"
              value={newEvent.time}
              onChange={(e)=>setNewEvent({...newEvent,time:e.target.value})}
            />

            <TextField fullWidth margin="dense" type="number"
              label="Цена"
              value={newEvent.price}
              onChange={(e)=>setNewEvent({...newEvent,price:e.target.value})}
            />

            <FormControl fullWidth margin="dense">
              <InputLabel>Мастер</InputLabel>
              <Select
                value={newEvent.master_id}
                label="Мастер"
                onChange={(e)=>setNewEvent({...newEvent,master_id:e.target.value})}
              >
                {masters.map(m=>(
                  <MenuItem key={m.id} value={m.id}>{m.name}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </DialogContent>

          <DialogActions>
            {editingId && (
              <Button color="error" onClick={deleteAppointment}>
                Удалить
              </Button>
            )}
            <Button onClick={()=>setDialogOpen(false)}>Отмена</Button>
            <Button onClick={saveEvent} variant="contained">
              Сохранить
            </Button>
          </DialogActions>
        </Dialog>

        {/* MASTER DIALOG */}
        <Dialog open={masterDialogOpen} onClose={()=>setMasterDialogOpen(false)}>
          <DialogTitle>
            {editingMasterId ? "Редактирование мастера" : "Новый мастер"}
          </DialogTitle>

          <DialogContent>
            <TextField fullWidth margin="dense"
              label="Имя"
              value={newMaster.name}
              onChange={(e)=>setNewMaster({...newMaster,name:e.target.value})}
            />

            <TextField fullWidth margin="dense"
              label="Телефон"
              value={newMaster.phone}
              onChange={(e)=>setNewMaster({...newMaster,phone:e.target.value})}
            />

            <TextField fullWidth margin="dense"
              type="number"
              label="Процент"
              value={newMaster.percent}
              onChange={(e)=>setNewMaster({...newMaster,percent:e.target.value})}
            />

            <TextField fullWidth margin="dense"
              type="color"
              label="Цвет"
              InputLabelProps={{ shrink:true }}
              value={newMaster.color}
              onChange={(e)=>setNewMaster({...newMaster,color:e.target.value})}
            />

            <TextField fullWidth margin="dense"
              label="URL аватара"
              value={newMaster.avatar}
              onChange={(e)=>setNewMaster({...newMaster,avatar:e.target.value})}
            />
          </DialogContent>

          <DialogActions>
            <Button onClick={()=>setMasterDialogOpen(false)}>Отмена</Button>
            <Button onClick={saveMaster} variant="contained">
              Сохранить
            </Button>
          </DialogActions>
        </Dialog>

      </Box>
    </ThemeProvider>
  );
}