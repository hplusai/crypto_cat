ts_1min=60000;
pairs={};
$min_usd=11;
usd_stables=['USDT','USDC','TUSD','BUSD'];

//fl_upd_info=true;//first time always sync pair settings with server

function auto_settings(title, price,onAply,onCancel){
    $('<div id="auto_params"></div>').dialog({
        modal: true,
        title: title,
        open: function () {
            var markup = `
  <span>Sell%:<input type="number" id="d_profit" value="${$('#profit').val()}" /></span><br/>
  <span>Rebuy%:<input type="number" id="d_rebuy" value="${$('#rebuy').val()}" /></span><br/>
  <span>Amo%:<input type="number" id="d_amo" value="${$('#token_amo_percent').val()}" /></span><br/>
  <span>Start Price:<input type="number" id="d_price" value="${price}" /></span>`;
            $(this).html(markup);
        },
        close: function(event, ui)
        {
            $(this).dialog('destroy').remove();
        },
        buttons: {
            Apply: function () {
		if (onAply!=null) onAply();
                $(this).dialog("close");
		$(this).remove()
            },
            Cancel: function () {
		if (onCancel!=null) onCancel();
                $(this).dialog("close");	
            }
        }
    }); //end confirm dialog
}

function trade_params(title, onAply, onCancel){
    $('<div id="trade_params"></div>').dialog({
        modal: true,
        title: title,
        open: function () {
            var markup = `<div>
  <input type="radio" id="oper_buy" name="trade_oper" value="buy" checked>
  <label for="oper_buy">Buy</label>
  <input type="radio" id="oper_sell" name="trade_oper" value="sell">
  <label for="oper_sell">Sell</label>
</div><br/>
<span>Amo$(in $,+buy,-sell):<input type="number" id="t_amo" value="${$min_usd}" />$</span>`
            $(this).html(markup);
            $('input[type=radio][name=trade_oper]').change(function() {
              if (this.value == 'buy') {
                $('#t_amo').val(Math.abs($('#t_amo').val()));
	      }
              else if (this.value == 'sell') {
                $('#t_amo').val(-Math.abs($('#t_amo').val()));
    	     };
            });
        },
        close: function(event, ui)
        {
            $(this).dialog('destroy').remove();
        },
        buttons: {
            Apply: function () {
		if (onAply!=null) onAply();
                $(this).dialog("close");
            },
            Cancel: function () {
		if (onCancel!=null) onCancel();
                $(this).dialog("close");	
            }
        }
    }); //end confirm dialog
}


function get_bal(tok){
  if (tok.name=='USDT') return tok.amo.toFixed(2)+'$';
  return tok.usd.toFixed(2)+'$ ('+tok.amo+')';
}

function fltTokens(){
  // Declare variables
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("t_search");
  filter = input.value.toUpperCase();
  table = document.getElementById("pairs");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}

function post_upd($t,symb,mode,price,profit,rebuy,act_amo){
  let pair=pairs[symb];
  pair.last_p=price;
  pair.mode=mode;
  pair.profit=profit;
  pair.rebuy=rebuy;
  pair.sell_price=pair.last_p*(1+profit/100.0);
  pair.buy_price=pair.last_p*(1-rebuy/100.0);
  pair.act_amo=act_amo;
  pair.key=$('#n_api_key').val();
  pair.secret=$('#n_api_sec').val();
  pair.tg_token=$('#tg_token').val();
  pair.tg_chat_id=$('#tg_chat_id').val();
//  pair.dc_url=$('#dc_url').val();
  pair.tok=pair.token.name
  pair.bas=pair.base.name
  if (mode!='auto') {
    $t.closest('tr').addClass('auto');
  };
  if (mode=='none') {
    $t.closest('tr').removeClass('auto');
  };
  $.post('upd',pair)
  .done(function() {
    upd_data();
//    alert( "second success" );
  })
  .fail(function() {
    alert( "error" );
//    fl_upd_info=false;
    upd_info();
  });
}

function set_mode($t,mode){
  let symb=$t.parent().parent().attr('id');
//  let tick=$ticks[symb];
//  let price=tick.last;
  let price=pairs[symb].price;
  if (mode=='auto') {
    auto_settings(symb+' - auto', price,function(){
      console.log($('#d_price').val());
      post_upd($t,symb,mode,$('#d_price').val(),$('#d_profit').val(),$('#d_rebuy').val(),$('#d_amo').val());
    });
  };
  if (mode=='none') {
    post_upd($t,symb,mode,price,$('#profit').val(),$('#rebuy').val(),$('#token_amo_percent').val());
  };
//  console.log(sId);
}

function trade($t){
  let symb=$t.parent().parent().attr('id');
  let price=pairs[symb].price;
  trade_params(symb+' - market order',function(){
    let usd=$('#t_amo').val();
    console.log(usd);
    let base=pairs[symb].base.name;
    let amo=0;
    if (base=='USDT') {
      amo=usd/price;
    }
    else {
      let upair=base+'USDT';
      if (upair in pairs) {
        in_bas=usd/pairs[upair].price;
        amo=in_bas/price;
      }
      else {
       alert('Cannot find '+upair);
       return;
      }
    };
    console.log(amo);
//    return;
//    fl_upd_info=false;
    $.post('trade',{symbol:symb,amo:amo, key:$('#n_api_key').val(), secret:$('#n_api_sec').val(),tg_token:$('#tg_token').val(),tg_chat_id:$('#tg_chat_id').val()})
    .done(function() {
      upd_info();
//    alert( "second success" );
    })
    .fail(function() {
      alert( "error" );
      upd_info();
    });
 });
}

function add_rec(pair, _class){
//  symb=tok+'/'+base;
//  if (hide_inactive && (group.bal$()==0)) return;
  let change=0;
  let volume=0;
  let price=pair.price;
  let spec_class='';
  let small_balance=$min_usd*2;
  if (pair.token.usd<small_balance) {
    spec_class='small_bal';
  };
  let sMode=``;
  if (pair.mode=='none') {
    sMode+=`<input class='right' type="button" onclick="set_mode($(this),'auto')" value="Start"></input>`;
  };
  if (pair.mode=='auto') {
    sMode+=`<input class='right' type="button" onclick="set_mode($(this),'none')" value="Stop"></input>`;
    spec_class='auto';
  };
  sMode+=`<input class='right' type="button" onclick="trade($(this))" value="Trade"></input>`;

  let prev_price=pair.last_p;//ds(price_sid);
  let info='<td></td>';
  if (prev_price!=null) {
    let diff=price-prev_price;
    let perc=((price/prev_price)-1)*100;
    info=`<td class='${num_color(diff)}'>${price}<br/>Change: ${diff.toFixed(3)}(${perc.toFixed(3)}%)</td>`;
  };
  let last_trade='';
  if (pair.mode=='auto') {
    last_trade=`${pair.last_p}<br/><span><span class='green'>${pair.rebuy}%</span>,<span class='red'>${pair.profit}%</span>,<span class='blue'>${pair.act_amo}%</span></span>`;
  };
  let hint=`Next buy: ${pair.buy_price}&#013;Next sell: ${pair.sell_price}`;
//  console.log(last_trade);
  srec=`<tr class='${spec_class} ${_class}' id="${pair.symbol}" style='display:block'><td>${pair.token.name}${sMode}</td><td>${get_bal(pair.token)}</td><td>${pair.base.name}</td><td>${get_bal(pair.base)}</td><td title="${hint}">${last_trade}</td><td>${price}</td>${info}</tr>`;
  //body.append(srec);
//  ds(price_sid,price);
  return srec;
}

function check_acc(acc) {
  console.log('check_acc',acc.name);
}

function p_profit(){
  return +$('#profit').val();
}

function p_loss(){
  return +$('#loss').val();
}

function upd_data(){
//tickers
  let hide_inactive=$('#hide_inactive')[0].checked;
  let only_usd=$('#only_usd')[0].checked;
  let flt=$('#t_search').val().toUpperCase();
//  console.log(flt);
  let sbody='';
  for (const [k, pair] of Object.entries(pairs)) {
    if (only_usd && (usd_stables.indexOf(pair.base.name)<0)) continue;
    sbody+=add_rec(pair,'');
  };
  body=$('#pairs tbody').empty();
  body.append(sbody);
  fltTokens();
  if (hide_inactive) $('tr.small_bal').hide();
//  else $('tr.small_bal').show();
}

function get_upd_interval(){
  return Math.max(+$('#ctl_upd_interval').val(),2)*1000;
}

function upd_info(){
//  if (!fl_upd_info) return;
//  fl_upd_info=false;
  $.get('info', {key:$('#n_api_key').val(),secret:$('#n_api_sec').val()})
  .done(function(data) {
//    console.log(data);
    let arr=eval(data);
    let arr_sorted=arr.sort(function (a,b){
	bv=b.token.usd;
	if (b.mode=='auto') bv*=1000;
	av=a.token.usd;
	if (a.mode=='auto') av*=1000;
	return bv-av;
		});
    for (x of arr_sorted) {
      pairs[x.symbol]=x;
    };
//    console.log(pairs);
    upd_data();
  })
  .error(function(xhr, status, error) {
    alert(xhr.responseText);
//    var err = eval("(" + xhr.responseText + ")");
//    alert(err.Message);
  });
//  .fail(function() {
//    alert( "error" );
//  });
}

$(function(){
  load_store();
  $('#hide_inactive,#only_usd').change(function() {
    upd_data();
  });
  $('#t_search').keyup(function() {
    upd_data();
  });
  upd_info();
  setInterval(upd_info,1000*$('#ctl_upd_interval').val());
});
