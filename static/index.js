window.app = new Vue({
    el: '#app',
    data: {
        hello: "Hello"
    },
    methods: {
        test(){
            console.log(this.hello);
        }
    }
})