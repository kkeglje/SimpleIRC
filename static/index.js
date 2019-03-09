Vue.component('modal',{
    template: '#modal-template'
})

window.app = new Vue({
    el: '#app',
    data: {
        users: [],
        user: "",
        showModal: true,
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
                    app.updateUsers()
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
            axios
                .post('/addMessage',{'channel':channel,'name':usr,'msg':message,'time':t})
                .then(response=>(console.log(response.data['message']),app.updateMessages()))
            document.getElementById("messageInput").value="";
        },
        updateMessages(){
            axios
                .get('/getMessages',{'channel':app.activeChannel})
                .then(response =>(app.messages = response.data['messages']))
        }
    },
    created(){
        this.interval = setInterval(() => this.updateUsers(), 5000); //refresh users every 5 seconds
        this.interval = setInterval(() => this.updateMessages(),1000); //refresh messages ever second
    }
})
window.onbeforeunload = app.removeUser;

