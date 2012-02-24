import httplib
import urllib
from xml.dom.minidom import parseString


class MobilCibClient:
  def __init__(self, username, password):
    self.conn = httplib.HTTPSConnection("m.cib.hu")
    # get jsessionid
    self.conn.request("GET", "/mobilCIB/")
    resp = self.conn.getresponse()
    cookie = resp.getheader('set-cookie')
    self.jsessionid = cookie.split('JSESSIONID=')[1].split(';')[0]

    # get ticket
    resp = self._req("/mobilCIB/frame.jsp")
    body = resp.read()
    self.ticket = body.split("tckt=")[1].split('"')[0]

    # login
    self.param_s = 'frame.jsp'
    self.param_f = 'mobile.function.login:LoginRequest'
    self.login(username, password)

  def _req(self, path, get_params=None, post_params=None, ticket=None):

    url = "%s;jsessionid=%s" % (path, self.jsessionid)
    if get_params:
      url += '?%s' % get_params
    if ticket:
      if get_params:
        url += '&tckt=%s' % ticket
      else:
        url += '?tckt=%s' % ticket
    headers = {
      "Cookie": "skin=default; browserOK=resultsuccess; locale=HU; JSESSIONID=%s" % self.jsessionid,
      "User-Agent": "Android",
    }
    if post_params is None: # GET
      print 'GET %s' % url
      print headers
      self.conn.request("GET", url, None, headers)
    else: # POST
      headers["Content-type"] = "application/x-www-form-urlencoded"
      print 'POST %s' % url
      print post_params
      print headers
      self.conn.request("POST", url, post_params, headers)
    resp = self.conn.getresponse()
    return resp

  def dispatcher_req(self, param_t, form_params=None):
    if self.param_f in ('mobile.function.login:LoginRequest', 'null'):
      ticket = self.ticket
    else:
      ticket = None

    if form_params:
      fparams = {}
      for param in form_params:
        ffunction = ''
        if self.param_f[0].isupper(): # function name needs path
          ffunction += '_46_'.join(self.param_s.split('/')[:-1]) + '_58_'
        ffunction += self.param_f.replace('.', '_46_').replace(':', '_58_')
        fparam = '$$%s$$%s$$%s' % (param, ffunction, ffunction)
        fparams[fparam] = form_params[param]
      post_data = urllib.urlencode(fparams)
    else:
      post_data = None
    response = self._req('/mobilCIB/dispatcher', "_T_=%s&_S_=%s&_F_=%s" % (param_t, self.param_s, self.param_f), post_data, ticket)
    return response
  
  def login(self, username, password):
    self.dispatcher_req('/mobile/function/login/loginprocess.jsp', {'LoginId': username, 'Password': password})
    self.param_s = 'menu.jsp'
    self.param_f = 'mobile.function.menu'
  
  
  # Szamlaegyenleg
  def getAccountOverview(self):
    self.param_s = 'menu.jsp'
    self.param_f = 'mobile.function.menu'
    response = self.dispatcher_req('/mobile/function/accountoverview/accountoverview_1.jsp')
    return response
    
  def getAccountDetails(self, accountnumber):
    self.param_s = 'mobile/function/accountoverview/accountoverview_1.jsp'
    self.param_f = 'AccountOverViewPage'
    response = self.dispatcher_req('/mobile/function/accountoverview/accountoverview_2.jsp', {
      'AccountNumber': accountnumber
    })
    return response
        
  
  # Szamlatortenet
  def getAccountinfo(self):
    self.param_s = 'menu.jsp'
    self.param_f = 'mobile.function.menu'
    response = self.dispatcher_req('/mobile/function/accountinfo/accountinfo_1.jsp')
    return response

  def setAccountInterval(self, accountnumber, interval='onemonth'):
    # interval: 'oneweek', 'twoweeks', 'onemonth', 'user'
    self.param_s = 'mobile/function/accountinfo/accountinfo_1.jsp'
    self.param_f = 'AccountIntervalPage'
    response = self.dispatcher_req('/mobile/function/accountinfo/accountinfo_2.jsp', {
      'AccountNumber': accountnumber,
      'Interval': interval
    })
    return response
    
  def setTransactiontypeAmount(self, minamount='', maxamount='', transactiontype='both'):
    # minamount, maxamount: '', '[0-9]*'
    # transactiontype: 'credit', 'debit', 'both'
    self.param_s = 'mobile/function/accountinfo/accountinfo_2.jsp'
    self.param_f = 'TransactiontypeAmountPage'
    response = self.dispatcher_req('/mobile/function/accountinfo/accountinfo_3.jsp', {
      'MinAmount': minamount,
      'MaxAmount': maxamount,
      'TransactionType': transactiontype
    })
    return response
    
  def setTransactiontypeAmountDate(self, fromdate, todate, minamount='', maxamount='', transactiontype='both'):
    # fromdate, todate: 'YYYY.MM.DD.'
    # minamount, maxamount: '', '[0-9]*'
    # transactiontype: 'credit', 'debit', 'both'
    self.param_s = 'mobile/function/accountinfo/accountinfo_2.jsp'
    self.param_f = 'TransactiontypeAmountDatePage'

    response = self.dispatcher_req('/mobile/function/accountinfo/accountinfo_3.jsp', {
      'FromDate': fromdate,
      'ToDate': todate,
      'MinAmount': minamount,
      'MaxAmount': maxamount,
      'TransactionType': transactiontype
    })
    return response
    
  def getAccountHistoryItem(self, id=0):
    self.param_s = 'mobile/function/accountinfo/accountinfo_3.jsp'
    self.param_f = 'AccountHistoryItem'
    response = self.dispatcher_req('/mobile/function/accountinfo/accountinfo_4.jsp', {
      'Id': id
    })
    return response


  # Hitel-, bevasarlokartya attekinto
  def getCreditcardoverview(self):
    self.param_s = 'menu.jsp'
    self.param_f = 'mobile.function.menu'
    response = self.dispatcher_req('/mobile/function/creditcardoverview/creditcardoverview_1.jsp')
    return response


  # Eseti atutalas
  def getPayment(self):
    self.param_s = 'menu.jsp'
    self.param_f = 'mobile.function.menu'
    response = self.dispatcher_req('/mobile/function/payment/payment_1.jsp')
    return response
    
  def setSourceAccount(self, sourceaccountnumber):
    self.param_s = 'mobile/function/payment/payment_1.jsp'
    self.param_f = 'SourceAccountPage'
    response = self.dispatcher_req('/mobile/function/payment/payment_2.jsp', {
      'SourceAccountNumber': sourceaccountnumber
    })
    return response
    
  def setTargetAccount(self, targetaccountnumber, partnername=''):
    self.param_s = 'mobile/function/payment/payment_2.jsp'
    self.param_f = 'TargetAccountPage'
    response = self.dispatcher_req('/mobile/function/payment/payment_4.jsp', {
      'TargetAccountNumber': targetaccountnumber,
      'PartnerName': partnername
    })
    return response

  def setOthers(self, amount, paymentreference=''):
    # amount: '1000'
    # paymentreference: 'kozlemeny'
    self.param_s = 'mobile/function/payment/payment_4.jsp'
    self.param_f = 'OthersPage'
    response = self.dispatcher_req('/mobile/function/payment/payment_forecast.jsp', {
      'Amount': amount,
      'PaymentReference': paymentreference
    })
    return response
    
  def setSecondLevelAuthenticationRequest(self, password):
    self.params_s = 'mobile/function/payment/payment_forecast.jsp'
    self.params_f = 'mobile:SecondLevelAuthenticationRequest'
    response = self.dispatcher_req('/mobile/function/payment/payment_result.jsp', {
      'Password': password
    })
    return response
    
  # Betet
  
  # Kartyalimitek
  
  # Mobilfeltoltes
  
  # Jelszomodositas
  
  # Kilepes
  
  
  def parseAccounts(self):
    accounts = {}
    page = self.getAccountOverview().read()
    print page
    accountoverview = parseString(page)
    for tr in accountoverview.getElementsByTagName('table')[0].getElementsByTagName('tr'):
      href = tr.getElementsByTagName('td')[0].getElementsByTagName('a')[0].getAttribute('href')
      szamlaszam = href.split("'")[-2]
      
      accountdetails = parseString(self.getAccountDetails(szamlaszam).read())
      szamlanev = accountdetails.getElementsByTagName('div')[5].firstChild.wholeText
      elerheto = accountdetails.getElementsByTagName('td')[1].firstChild.wholeText
      zarolt = accountdetails.getElementsByTagName('td')[4].firstChild.wholeText
      hitelkeret = accountdetails.getElementsByTagName('td')[7].firstChild.wholeText
      accounts[szamlaszam] = {
        'szamlaszam': szamlanev,
        'elerheto': elerheto,
        'zarolt': zarolt,
        'hitelkeret': hitelkeret
      }
    return accounts

