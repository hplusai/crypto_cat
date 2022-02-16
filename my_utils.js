function cur_time_stamp(){
  date = new Date();
  return date.getTime();
}

function ds(par=null, val=null){
  if (par!=null){
//     if (localStorage.getItem(par) === null) localStorage[par]=val;
     if (val===null) {
        val=localStorage.getItem(par);
//        console.log(par,'ret',val);
        if (val=="[object Object]") return null;
	return JSON.parse(val);
     };
     localStorage[par]=JSON.stringify(val);
     return JSON.parse(localStorage[par]);
  }
  return localStorage;
}

function num_color(n,n_max=0){
/*  col='#FF6347';
  if (n>0) col='#32CD32';*/
  if (n==n_max) return 'gray';
  if (n>n_max) return 'green'
  else return 'red';
}

function asleep(ms) {
  return new Promise(
    resolve => setTimeout(resolve, ms)
  );
}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function Msg(s){
  if ($('#use_voice')[0].checked) {
    say(s,'en-us');
  };
}

function has(d,k){
  return d.hasOwnProperty(k);
}

function cap_str(s){
  return s && s[0].toUpperCase() + s.slice(1);
}
