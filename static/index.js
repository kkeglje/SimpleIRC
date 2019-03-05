Vue.component('modal',{
    template: '#modal-template'
})

window.app = new Vue({
    el: '#app',
    data: {
        users:[],
        showModal: true,
        error: null
    },
    delimiters: ['[[',']]'],
    methods: {
        newUser(){
            var user = document.getElementById("guestName").value;
            console.log(user);
            this.users.forEach(element => {
                if(element==user){
                    this.showModal = true;
                    error = "User with that name already exists!";
                    return
                }
            });
            this.users.push(user);

        }
    }
})