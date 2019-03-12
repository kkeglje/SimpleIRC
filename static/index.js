Vue.component('modal',{
    template: '#modal-template'
})

window.app = new Vue({
    el: '#app',
    data: {
        users: [],
        user: "",
        showModal: true,
        showroomModal:false,
        error: 'false',
        messages: [],
        rooms:["Home","Learning"],
        activeChannel: "Home"
    },
    delimiters: ['[[',']]'],
    methods: {
        newUser(){
            app.user = document.getElementById("guestName").value
            axios
                .post('/addUser',{'guestName' : app.user})
                .then(
                    function(response){
                        if(response.data['status'] == 200){
                            app.users.push(app.user);
                            app.showModal = false;
                            app.error = 'false';
                        }
                        else{
                            app.showModal = true;
                            app.error = response.data['message'];
                            console.log(this.error);
                        };
                    },
                    app.updateRooms(),
                    app.updateUsers(),
                    app.interval = setInterval(() => app.updateMessages(),1000) //refresh messages ever second

                )
        },
        updateUsers(){
            axios
                .get('/getUsers')
                .then(
                    response => (app.users = response.data['users'])
                )
        },
        removeUser(){
            axios
                .post('/removeUser',{'guestName': app.user})
        },
        handleEnter(e){
            if(e.keyCode === 13){
                this.sendMessage();
            }
        },
        sendMessage(){
            var channel = app.activeChannel
            var usr = app.user
            var message = document.getElementById("messageInput").value
            var t = new Date()
            t = `${t.getFullYear()}:${t.getMonth()+1}:${t.getDate()}:${t.getHours()}:${t.getMinutes()}:${t.getSeconds()}`
            console.log(`${channel} ${this.activeChannel}`)
            axios
                .post('/addMessage',{'channel':channel,'name':usr,'msg':message,'time':t})
                .then(response=>(console.log(response.data['message']),app.updateMessages()))
            document.getElementById("messageInput").value="";
        },
        updateMessages(){
            axios
                .get('/getMessages',{params: {'channel':app.activeChannel}})
                .then(response =>(app.messages = response.data['messages']))
        },
        changeChannel(name){
            this.activeChannel = name;
            app.updateMessages()
        },
        addChannel(){
            roomName = document.getElementById("roomName").value
            console.log(roomName)
            axios
                .post('/addChannel', {'channel':roomName})
                .then(
                    function(r){
                        if(r.data['status']==201){
                            app.rooms.push(roomName)
                        }else{
                            console.log(r.data['message'])
                        }
                },app.showroomModal=false)
        },
        updateRooms(){
            axios
                .get('/getChannels')
                .then(response=>(app.rooms = response.data['channels'].split('|')))
        }
    },
    created(){
        this.interval = setInterval(() => this.updateUsers(), 5000); //refresh users every 5 seconds
        this.interval = setInterval(() => this.updateRooms(),5000); //refresh channels every 5 sec
    }
})
window.onbeforeunload = app.removeUser;

