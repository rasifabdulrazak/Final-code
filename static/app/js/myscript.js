$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 1,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 3,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 5,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$('.plus-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = this.parentNode.children[2]
    $.ajax({
        type : "GET",
        url : "/plus_cart",
        data : {
            cart_id : id
        },
        success : function(data){
            if (data.flag == 0){
                swal.fire("Stock Limit", "Only this much stock", "info");
            }
            else{
                eml.innerText = data.quantity
                document.getElementById("amount").innerText = data.amount
                document.getElementById("totalamount").innerText = data.total_amount
            }
            
            
        }
    })
})

$('.minus-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = this.parentNode.children[2]
    console.log(id)
    $.ajax({
        type : "GET",
        url : "/minus_cart",
        data : {
            cart_id : id
        },
        success : function(data){
            eml.innerText = data.quantity
            document.getElementById("amount").innerText = data.amount
            document.getElementById("totalamount").innerText = data.total_amount
        }
    })
})

$('.remove-cart').click(function(){
    var id = $(this).attr("pid").toString();
    var eml = this
    console.log(id)
    $.ajax({
        type : "GET",
        url : "/remove_cart",
        data : {
            cart_id : id
        },
        success : function(data){
            location.reload(true);
            document.getElementById("amount").innerText = data.amount
            document.getElementById("totalamount").innerText = data.total_amount
            
        }
    })
})