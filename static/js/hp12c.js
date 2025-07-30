// --- Busca OpenAI integrada ---
const btn = document.getElementById('hp12c-search-btn');
const clearBtn = document.getElementById('hp12c-clear-btn');
const input = document.getElementById('hp12c-search-input');
const resp = document.getElementById('hp12c-response');
btn.onclick = async function(){
  const question = input.value.trim();
  if (!question) return;
  resp.innerHTML = 'Pensando...';
  try {
    const res = await fetch("/openai-assistente", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({pergunta: question})
    });
    const data = await res.json();
    resp.innerHTML = data.resposta || 'Erro na resposta do servidor';
  } catch (e) {
    resp.innerHTML = "Erro ao conectar com o backend";
  }
}
clearBtn.onclick = function() {
  input.value = '';
  resp.innerHTML = '';
  input.focus();
}

// --- Calculadora HP12C fiel + CFj/Nj/IRR/NPV ---
const display = document.getElementById('calc-display');
let stack = [0,0,0,0];
let current = '';
let memory = Array(20).fill(0);
let modeBeg = false;
let cashflows = []; // {valor: Number, nj: Number}
let awaitingNj = false;

// --- Variáveis financeiras individuais ---
let valN = null, valI = null, valPV = null, valPMT = null, valFV = null;

function updateDisplay(msg) {
  if (msg) { display.value = msg; return; }
  display.value = current !== '' ? current : stack[0];
}
function pushStack(val) { stack = [val, stack[0], stack[1], stack[2]]; }
function popStack() { let x = stack[0]; stack = [stack[1], stack[2], stack[3], 0]; return x; }
function swapXY() { [stack[0], stack[1]] = [stack[1], stack[0]]; }
function clearStack() { stack = [0,0,0,0]; }
function showError(msg) { updateDisplay("Erro: " + msg); setTimeout(updateDisplay, 2000, ""); }
function clearFinancialMemory() { valN = valI = valPV = valPMT = valFV = null; }

// -- Nova solveFinancial fiel à HP12C --
function solveFinancial(key) {
  // Salva valor digitado na variável correta
  let val = current !== '' ? parseFloat(current) : stack[0];
  if (isNaN(val)) return showError("Digite um valor válido");

  // Salva no registro apropriado
  if (key === 'n')   valN = val;
  if (key === 'i')   valI = val;
  if (key === 'PV')  valPV = val;
  if (key === 'PMT') valPMT = val;
  if (key === 'FV')  valFV = val;
  current = '';

  // Conta quantos campos foram preenchidos
  let filled = [valN, valI, valPV, valPMT, valFV].filter(v=>v!==null).length;
  if (filled < 4) { updateDisplay(); return; } // Não tenta calcular ainda!

  let n = valN, i = valI, pv = valPV, pmt = valPMT, fv = valFV, beg = modeBeg ? 1 : 0;
  let missing = null, result = null;

  // Descobre qual campo calcular (está nulo)
  if (valN  === null) missing = 'n';
  if (valI  === null) missing = 'i';
  if (valPV === null) missing = 'PV';
  if (valPMT=== null) missing = 'PMT';
  if (valFV === null) missing = 'FV';

  try {
    if (missing === 'i') {
      // Cálculo iterativo de i
      let guess = 0.1, iter=0, test=0, res=0;
      while(iter++<100) {
        if(guess===-1) break;
        test = pv*Math.pow(1+guess,n) + pmt*((1+guess*beg)*(Math.pow(1+guess,n)-1)/guess) + fv;
        if(Math.abs(test)<1e-7) break;
        res = pv*n*Math.pow(1+guess,n-1) + pmt*((1+guess*beg)*n*Math.pow(1+guess,n-1)/guess-(1+guess*beg)*(Math.pow(1+guess,n)-1)/Math.pow(guess,2));
        guess -= test/(res||1);
      }
      result = guess*100;
      valI = result;
      updateDisplay(result.toFixed(8));
    }
    else if (missing === 'n') {
      i = i/100;
      result = Math.log((pmt*(1+i*beg)-fv*i)/(pmt*(1+i*beg)+pv*i))/Math.log(1+i);
      valN = result;
      updateDisplay(result.toFixed(8));
    }
    else if (missing === 'PV') {
      i = i/100;
      result = (-pmt*(1+ i*beg)*(Math.pow(1+i,n)-1)/(i*Math.pow(1+i,n))) - (fv/Math.pow(1+i,n));
      valPV = result;
      updateDisplay(result.toFixed(8));
    }
    else if (missing === 'PMT') {
      i = i/100;
      result = (-pv*i*Math.pow(1+i,n)-fv*i)/( (1+i*beg)*(Math.pow(1+i,n)-1) );
      valPMT = result;
      updateDisplay(result.toFixed(8));
    }
    else if (missing === 'FV') {
      i = i/100;
      result = -pv*Math.pow(1+i,n) - pmt*(1+i*beg)*(Math.pow(1+i,n)-1)/i;
      valFV = result;
      updateDisplay(result.toFixed(8));
    }
    else {
      updateDisplay("Todos preenchidos!");
    }
    // Atualiza stack também
    stack[0] = result;
  } catch(e) {
    showError("Cálculo inválido");
  }
}

function updateBegEndBtn() {
  let begBtn = document.querySelector('.calc-btn[data-key="BEG"]');
  if(!begBtn) return;
  begBtn.style.background = modeBeg ? "#ffbb00" : "#232323";
  begBtn.textContent = modeBeg ? "BEG*" : "BEG";
}

// --- Funções Avançadas: CFj, Nj, IRR, NPV ---
function clearCashflows() {
  cashflows = [];
  awaitingNj = false;
}
function handleCFj() {
  let val = current !== '' ? parseFloat(current) : stack[0];
  if (isNaN(val)) return showError("Digite o valor do fluxo");
  cashflows.push({valor: val, nj: 1});
  awaitingNj = true;
  updateDisplay("CFj " + val);
  current = '';
  setTimeout(updateDisplay, 1300);
}
function handleNj() {
  if (!awaitingNj || !cashflows.length) return showError("Digite um CFj primeiro");
  let njval = current !== '' ? parseInt(current) : 1;
  if (isNaN(njval) || njval < 1) return showError("Nj inválido");
  cashflows[cashflows.length-1].nj = njval;
  awaitingNj = false;
  updateDisplay("Nj " + njval);
  current = '';
  setTimeout(updateDisplay, 1300);
}
function handleNPV() {
  if (!cashflows.length) return showError("Entre com fluxos CFj antes");
  let taxa = prompt("Taxa (%) ao período?");
  if (taxa===null) return;
  taxa = parseFloat(taxa);
  if(isNaN(taxa)) return showError("Taxa inválida");
  taxa /= 100;
  let npv = 0, idx = 0;
  for(let i=0;i<cashflows.length;i++) {
    for(let j=0;j<cashflows[i].nj;j++,idx++)
      npv += cashflows[i].valor / Math.pow(1+taxa, idx);
  }
  updateDisplay("NPV = " + npv.toFixed(8));
  clearCashflows();
  setTimeout(updateDisplay, 2500, "");
}
function handleIRR() {
  if (!cashflows.length) return showError("Entre com fluxos CFj antes");
  let fluxo = [];
  cashflows.forEach(cf=>{
    for(let j=0;j<cf.nj;j++) fluxo.push(cf.valor);
  });
  // Algoritmo Newton-Raphson
  let guess = 0.1, iter=0, res=0, deriv=0, eps=1e-8, maxiter=200;
  for(;iter<maxiter;iter++) {
    res = 0; deriv = 0;
    for(let k=0;k<fluxo.length;k++) {
      res += fluxo[k] / Math.pow(1+guess, k);
      if (k>0) deriv -= k*fluxo[k]/Math.pow(1+guess, k+1);
    }
    if(Math.abs(res)<eps) break;
    guess -= res/(deriv||1);
    if(guess<-0.99) { guess=0.01; }
  }
  if(isFinite(guess)) {
    updateDisplay("IRR = "+ (guess*100).toFixed(8)+"%");
  } else {
    showError("IRR não encontrado");
  }
  clearCashflows();
  setTimeout(updateDisplay, 2500, "");
}

document.querySelectorAll('.calc-btn').forEach(btn => {
  btn.onclick = function(){
    const k = btn.dataset.key;
    if(!k) return;

    // Novos botões avançados
    if (k==='CFj') return handleCFj();
    if (k==='Nj')  return handleNj();
    if (k==='NPV') return handleNPV();
    if (k==='IRR') return handleIRR();

    if(!isNaN(k) || k=='.') {
      if(current.length<14) current += k;
      updateDisplay();
    }
    else if(k==='ENTER') {
      if(current!=='') pushStack(parseFloat(current));
      current = '';
      updateDisplay();
    }
    else if(['+','-','×','÷'].includes(k)) {
      if(current!=='') { pushStack(parseFloat(current)); current=''; }
      let y = popStack(), x = popStack(), r=0;
      if     (k==='+') r = x+y;
      else if(k==='-') r = x-y;
      else if(k==='×') r = x*y;
      else if(k==='÷') {
        if (y===0) return showError("Divisão por zero");
        r = x/y;
      }
      pushStack(r);
      updateDisplay();
    }
    else if(k==='CHS') {
      if(current!=='') { current = (-parseFloat(current)).toString(); }
      else { stack[0]*=-1; }
      updateDisplay();
    }
    else if(k==='CLx') {
      current = '';
      stack[0] = 0;
      updateDisplay();
    }
    else if(k==='CLr') {
      clearStack();
      current = '';
      updateDisplay();
      clearCashflows();
      clearFinancialMemory();
    }
    else if(k==='X<>Y') {
      swapXY(); updateDisplay();
    }
    else if(k==='1/x') {
      let v = current!=='' ? parseFloat(current) : stack[0];
      if(v!==0) {
        v = 1/v;
        current!=='' ? current=v.toString() : stack[0]=v;
        updateDisplay();
      } else showError("Divisão por zero");
    }
    else if(k==='√x') {
      let v = current!=='' ? parseFloat(current) : stack[0];
      if(v>=0) {
        v = Math.sqrt(v);
        current!=='' ? current=v.toString() : stack[0]=v;
        updateDisplay();
      } else showError("Raiz de número negativo");
    }
    else if(k==='%') {
      let y = popStack(), x = popStack();
      let r = y * x / 100;
      pushStack(r); updateDisplay();
    }
    else if(k==='Δ%') {
      let y = popStack(), x = popStack();
      let r = ((y-x)/x)*100;
      pushStack(r); updateDisplay();
    }
    else if(k==='STO') {
      let reg = prompt("Salvar em qual registro? (0-19)");
      if(reg!==null && !isNaN(reg) && reg>=0 && reg<20) memory[reg]=stack[0];
    }
    else if(k==='RCL') {
      let reg = prompt("Ler qual registro? (0-19)");
      if(reg!==null && !isNaN(reg) && reg>=0 && reg<20) { stack[0]=memory[reg]; updateDisplay();}
    }
    else if(k==='EEX') {
      let v = current!=='' ? parseFloat(current) : stack[0];
      let exp = prompt("Expoente:");
      if(exp!==null && !isNaN(exp)) {
        v = v * Math.pow(10,parseInt(exp));
        current!=='' ? current=v.toString() : stack[0]=v;
        updateDisplay();
      }
    }
    else if(k==='BEG') {
      modeBeg = !modeBeg;
      updateBegEndBtn();
      updateDisplay(modeBeg ? "Modo BEG (início)" : "Modo END (fim)");
      setTimeout(()=>updateDisplay(),1300);
    }
    else if(['n','i','PV','PMT','FV'].includes(k)) {
      solveFinancial(k);
    }
    else if(k==='ON') {
      clearStack(); current=''; memory=Array(20).fill(0); updateDisplay(); clearCashflows(); clearFinancialMemory();
    }
    else if(['Σ+','Σ-','R/S'].includes(k)) {
      updateDisplay('Estatística');
      setTimeout(updateDisplay,1200);
    }
    else {
      updateDisplay('Função extra');
      setTimeout(updateDisplay,1200);
    }
  }
});
document.querySelectorAll('.calc-btn').forEach(btn=>{
  btn.addEventListener('touchstart',function(){
    const tip = btn.querySelector('.tooltip');
    if(tip) { tip.style.display='block'; setTimeout(()=>tip.style.display='none', 1500);}
  });
});
updateBegEndBtn();

