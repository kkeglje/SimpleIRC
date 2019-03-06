Vue.component('modal',{
    template: '#modal-template'
})

window.app = new Vue({
    el: '#app',
    data: {
        users: [],
        user: "",
        showModal: true,
        error: 'false'
    },
    delimiters: ['[[',']]'],
    methods: {
        newUser(){
            app.user = document.getElementById("guestName").value
            axios
                .post('addUser',{'guestName' : app.user})
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
                    response=>(app.users = response.data['users'])
                )
        },
        removeUser(){
            axios
                .post('/removeUser',{'guestName': app.user})
        }
    },
    created(){
        this.interval = setInterval(() => this.updateUsers(), 5000); //refresh users every 5 seconds
    }
})
window.onbeforeunload = app.removeUser;

