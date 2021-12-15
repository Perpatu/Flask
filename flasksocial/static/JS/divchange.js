function ChangeHome(div1, div2)
{
    let d1 = document.getElementById(div1);
    let d2 = document.getElementById(div2);
    if( d2.style.display === "none")
    {
        d1.style.display = "none";
        d2.style.display = "block";
    }
    else
    {
        d1.style.display = "block";
        d2.style.display = "none";
    }
}