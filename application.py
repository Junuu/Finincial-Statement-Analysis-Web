from flask import Flask ,render_template ,request
import requests
from bs4 import BeautifulSoup
from urllib import parse
import pandas as pd
from pandas import DataFrame as df
import html
import lxml
import time
from multiprocessing import freeze_support
from multiprocessing import Pool # Pool import하기

def make_yahoo_link(stock_name):
  finance_url = []  
  finance_url.append("https://finance.yahoo.com/quote/{}/financials?p={}".format(stock_name,stock_name))
  finance_url.append("https://finance.yahoo.com/quote/{}/balance-sheet?p={}".format(stock_name,stock_name))
  finance_url.append("https://finance.yahoo.com/quote/{}/cash-flow?p={}".format(stock_name,stock_name))
  return finance_url

def get_finance_content(get_finance_url):    
  stocks_url = requests.get(get_finance_url)
  html = stocks_url.text
  soup = BeautifulSoup(html, 'lxml')
  
  find_financials = get_finance_url.find('financials')
  find_balance = get_finance_url.find('balance')
  find_cash = get_finance_url.find('cash')
  # return 값은 항상 위에서 아래로 일정한 순서로 리스트에 들어감.
  get_title = soup.find("h1").get_text()  

  try:
    if find_financials != -1:
          
        total_revenue = []
        operating_income = []
        net_income = []

        get_info1 = soup.find_all("div","Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor) D(tbc)")
        get_info2 = soup.find_all("div","Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg D(tbc)")    


        total_revenue.append(get_info2[1].get_text())
        total_revenue.append(get_info1[1].get_text())
        total_revenue.append(get_info2[0].get_text())
        total_revenue.append(get_info1[0].get_text())        

        operating_income.append(get_info2[9].get_text())
        operating_income.append(get_info1[13].get_text())
        operating_income.append(get_info2[8].get_text())
        operating_income.append(get_info1[12].get_text())        

        net_income.append(get_info2[21].get_text())
        net_income.append(get_info1[31].get_text())
        net_income.append(get_info2[20].get_text())
        net_income.append(get_info1[30].get_text())          
      
        return total_revenue,operating_income,net_income

    if find_balance != -1:    
      working_capital = []
      debt_ratio = []    

      get_info1 = soup.find_all("div","Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor) D(tbc)")
      get_info2 = soup.find_all("div","Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg D(tbc)")
      
      debt_ratio.append(round(float(get_info2[3].get_text().replace(",",""))/float(get_info2[1].get_text().replace(",",""))*100,2))
      debt_ratio.append(round(float(get_info1[2].get_text().replace(",",""))/float(get_info1[0].get_text().replace(",",""))*100,2))
      debt_ratio.append(round(float(get_info2[2].get_text().replace(",",""))/float(get_info2[0].get_text().replace(",",""))*100,2))
      debt_ratio.append("-")      

      working_capital.append(get_info2[15].get_text())
      working_capital.append(get_info1[14].get_text())
      working_capital.append(get_info2[14].get_text())
      working_capital.append("-")      
      
      return debt_ratio,working_capital

    if find_cash != -1:
      sales_cash_flow = []
      invest_cash_flow = []
      finance_cash_flow = []

      get_info1 = soup.find_all("div","Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg Bgc($lv1BgColor) fi-row:h_Bgc($hoverBgColor) D(tbc)")
      get_info2 = soup.find_all("div","Ta(c) Py(6px) Bxz(bb) BdB Bdc($seperatorColor) Miw(120px) Miw(140px)--pnclg D(tbc)")

      sales_cash_flow.append(get_info2[1].get_text())
      sales_cash_flow.append(get_info1[1].get_text())
      sales_cash_flow.append(get_info2[0].get_text())
      sales_cash_flow.append(get_info1[0].get_text())          

      invest_cash_flow.append(get_info2[3].get_text())
      invest_cash_flow.append(get_info1[4].get_text())
      invest_cash_flow.append(get_info2[2].get_text())
      invest_cash_flow.append(get_info1[3].get_text())      

      finance_cash_flow.append(get_info2[5].get_text())
      finance_cash_flow.append(get_info1[7].get_text())
      finance_cash_flow.append(get_info2[4].get_text())
      finance_cash_flow.append(get_info1[6].get_text())
      
      return sales_cash_flow,invest_cash_flow,finance_cash_flow,get_title

  except:
    print("올바른 종목명을 입력해 주세요")
  
  return 4

def make_table(crwaling_result):
  table = '''
  기업명 : {}
  <br>
  <table>
  <thead>
    <tr>
      <th></th>
      <th>매출</th>
      <th>영업 이익</th>
      <th>당기 순이익</th>
      <th>부채비율</th>
      <th>운전자본</th>    
      <th>영업 활동으로 인한 현금 흐름</th>
      <th>투자 활동으로 인한 현금 흐름</th>
      <th>금융 활동으로 인한 현금 흐름</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2017</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      
    </tr>
    <tr>
      <td>2018</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      
    </tr>
    <tr>
      <td>2019</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      
    </tr>
    <tr>
      <td>TTM</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      <td>{}</td>
      
    </tr>
  </tbody>
  </table>
  <br>
  용어 설명
  <table>    
        
        <tr>
            <td>TTM</td>
            <td>Trailing twelve months의 약자로 지난 12개월을 의미합니다.</td>
        </tr>
        <tr>
            <td>당기 순이익</td>
            <td>기업이 벌어들이는 모든 이익에서 기업이 쓰는 모든 비용과 모든 손실을 뺀 차액</td>
        </tr>
        
        <tr>
            <td>부채비율</td>
            <td>기업의 자기자본에 대한 부채의 상대적 크기로 기업의 재무위험을 나타내는 지표</td>
        </tr>
        
        <tr>
            <td>유동부채</td>
            <td>1년안에 갚아야 하는 부채</td>
        </tr>
        <tr>
            <td>유동자산</td>
            <td>1년안에 현금화 할 수 있는 자산</td>
        </tr>
        <tr>
            <td>운전자본</td>
            <td>현금화가 쉬운 유동자산 에서 유동부채를 뺀 금액</td>
        </tr>
        
        <tr>
            <td>영업 활동으로 인한 현금흐름</td>
            <td>영업을 통하여 벌어들인 금액 +가 일반적인 기업</td>
        </tr>
        <tr>
            <td>투자 활동으로 인한 현금흐름</td>
            <td>투자 하는 금액의 흐름 -가 일반적인 기업</td>
        </tr>
        <tr>
            <td>재무 활동으로 인한 현금흐름</td>
            <td>돈을 갚거나 빌린 현금에 대한 흐름으로 돈을 갚는 -가 일반적인 기업</td>
        </tr>
    </table>    
  
  '''.format(crwaling_result[2][3],crwaling_result[0][0][0],crwaling_result[0][1][0],crwaling_result[0][2][0],crwaling_result[1][0][0],crwaling_result[1][1][0],crwaling_result[2][0][0],crwaling_result[2][1][0],crwaling_result[2][2][0],crwaling_result[0][0][1],crwaling_result[0][1][1],crwaling_result[0][2][1],crwaling_result[1][0][1],crwaling_result[1][1][1],crwaling_result[2][0][1],crwaling_result[2][1][1],crwaling_result[2][2][1],crwaling_result[0][0][2],crwaling_result[0][1][2],crwaling_result[0][2][2],crwaling_result[1][0][2],crwaling_result[1][1][2],crwaling_result[2][0][2],crwaling_result[2][1][2],crwaling_result[2][2][2],crwaling_result[0][0][3],crwaling_result[0][1][3],crwaling_result[0][2][3],crwaling_result[1][0][3],crwaling_result[1][1][3],crwaling_result[2][0][3],crwaling_result[2][1][3],crwaling_result[2][2][3])
  return table

def change_stock_to_code(stock): 
  try : #종목코드로 들어온 것
    if(stock == None):
        stock = "입력값이 없습니다."        
        return stock    
    int(stock)
    return stock
  except : # 종목코드가 아닌 어떤 문자가 들어오게되면 오류가 발생
    incode_stock=parse.quote(stock)
    search_url = "https://search.naver.com/search.naver?sm=top_hty&fbm=0&ie=utf8&query="
    search_url= search_url+incode_stock  
    stocks_url = requests.get(search_url)
    html = stocks_url.text
    soup = BeautifulSoup(html, 'lxml')
    search = soup.find_all("script") #script 구문을 모두 search에 저장    
    for i in range(0,len(search)): # 모든 script 구문을 돌아보며 sItemCode를 가진 script를 찾으면 break        
        if "sItemCode" in str(search[i]):
            break            
    # search[i] << 여기서 종목코드를 뽑아내야 함
    # string의 특정 단어 위치 찾기 https://hashcode.co.kr/questions/286/%EC%8A%A4%ED%8A%B8%EB%A7%81%EC%97%90-%ED%8A%B9%EC%A0%95-%EB%8B%A8%EC%96%B4-%EC%9C%84%EC%B9%98-%EC%B0%BE%EA%B8%B0
    # sItemCode의 index 찾기    
    st1 = str(search[i])
    st2 = "sItemCode"
    idx = st1.find(st2)     
    
    if idx==-1:
        if (stock[0] >= 'a' and stock[0] <= 'z') or (stock[0] >= 'A' and stock[0] <= 'Z'):          
          try:
            pool = Pool(processes=2) # 2개의 프로세스를 사용합니다.          
            crwaling_result=pool.map(get_finance_content, make_yahoo_link(stock))
            table=make_table(crwaling_result)
            return table
          except:
            print("올바르지 않은 종목명 입니다.")
          
          
        return "올바르지 않은 종목명 입니다."
    else:              
        stock = str(search[i])[idx+13:idx+19] #종목코드           
        try:
          int(stock)
          return stock #종목코드 return 
        except:          
          return "해당 증권정보는 종목코드가 없습니다."

def crawling(stock_code):
  URL = "https://finance.naver.com/item/main.nhn?code={}".format(stock_code)
  stocks_url = requests.get(URL)
  html = stocks_url.text
  soup = BeautifulSoup(html, 'lxml')
  info = ""
  result = ""
  # 재무제표가 없는 선물주식등은 분석이 불가능 ("기업실적분석" 이라는 string의 유무로 재무제표의 유무를 판단가능)
  # 예외처리

  #크롤링 부분
  #종목시세부분
  try:
    market_info=soup.find("dl","blind") #종목시세정보
    market_info=market_info.find_all("dd")         
  except:        
    return info,result,0,0,2

  

										
  info = info + "<details><summary>종목 시세 정보</summary><p>"         
  info = info + "<table>"   
          
  for i in range(0,len(market_info)):
    info = info + "<tr><td>"
    info = info + market_info[i].get_text()
    info = info + "</td></tr>"
    

  info = info + "</table>"
  info = info + "<br></p></details>"
   

  # 기업개요부분
  result = result + "<details><summary>기업 개요</summary><p>"         
  result = result + "<table>"
  try:
    summary_info = soup.find("div","summary_info") #기업개요 부분
    summary_info=summary_info.find_all("p")
    
    for i in range(0,len(summary_info)):
      result = result + "<tr><td>"
      result = result + summary_info[i].get_text()
      result = result + "</td></tr>"
    result = result + "</table>"
    result = result + "<br></p></details>"
  except:    
    result = result + "<tr><td>"
    result = result + "기업개요가 없습니다."
    result = result + "</td></tr>"
    result = result + "</table>"
    result = result + "<br></p></details>"

    

  #재무제표부분
  annual_date = []
  quarter_date = []
  attribute = []
  save_data = []

  try : 
    cas=soup.find("div","section cop_analysis") #재무제표 부분 cas = cop_analysis_section
    cas_rc=cas.find_all("th") #rc = row_columns
    cas_data=cas.find_all("td")
  except : #재무제표가 없을경우
        
    return info,result,0,0,0
  

  for i in range(3,7): #split() 함수를 사용하여 <br>\t 등 공백제거
    annual_date.append(cas_rc[i].get_text().split())

  for i in range(7,13):
    quarter_date.append(cas_rc[i].get_text().split())

  for i in range(23,39):
    attribute.append(cas_rc[i].get_text().split())

  for i in range(0,len(cas_data)):
    save_data.append(cas_data[i].get_text().split())



  #데이터를 모두 모았음으로 표를 만들면 됨 DataFrame 부분의 data= 뒷부분에 dictionary 가 필요함
  # DataFrame data 파트 만들기
  dict_data = dict()
  dict_list = []
  x = 0
  for i in range(0,len(attribute)):  
      dict_list.append([save_data[x],save_data[x+1],save_data[x+2],save_data[x+3],save_data[x+4],save_data[x+5],save_data[x+6],save_data[x+7],save_data[x+8],save_data[x+9]])
      x=x+(len(annual_date)+len(quarter_date)) # 년도와 분기의 개수 만큼 속성별 데이터묶음을 가져오도록 

  #DataFrame index부분 만들기
  try:
    index_list = [annual_date[0][0],annual_date[1][0],annual_date[2][0],annual_date[3][0],quarter_date[0][0],quarter_date[1][0],quarter_date[2][0],quarter_date[3][0],quarter_date[4][0],quarter_date[5][0]]
  except:        
    return info,result,0,0,1


  for i in range(0,len(attribute)):  #dictionary 만들기
    dict_data[str(attribute[i])] = dict_list[i]


  Financial_Statements = df(data=dict_data ,index = index_list)  
  return info,result,dict_list,market_info,Financial_Statements

def Financial_analysis(dict_list,market_info):
  analysis = ""
  if dict_list == 0 : #재무제표의 데이터가 부족한 경우
    return 0,0;  
  else:
  #dict_list의 요소들이 str이기 때문에 크기비교를 할 수 없음. 따라서 int로 변환해야하는데 -와 , 를 반영해야 할것
    for i in range(0,len(dict_list)):
      for j in range(0,len((dict_list[0]))):
        try:      
          dict_list[i][j][0]=dict_list[i][j][0].replace(",","") # 문자열의 ,를 ""아무것도 없는것으로 바꿔줌      
        except:  #빈 리스트들을 불러오거나 print하면 에러가 발생함 아래에서 비교할때 재무제표별로 무슨항목이 비어있는지 모르기때문에 각각 예외처리를 해줘야 함
          continue
        

    result = 0
    analysis = analysis + "<table>"
    #매출액 분석

    try:
      if(float(dict_list[0][0][0]) < float(dict_list[0][1][0]) and float(dict_list[0][1][0]) < float(dict_list[0][2][0])):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "매출액이 최근3년간 증가하고 있는 기업입니다."
        analysis = analysis  + "</td></tr>"
        result = result + 10
      elif(float(dict_list[0][0][0]) > float(dict_list[0][1][0]) and float(dict_list[0][1][0]) > float(dict_list[0][2][0])):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "매출액이 최근3년간 감소하고 있는 기업입니다."
        analysis = analysis  + "</td></tr>"
        
        result = result - 10
      else:
        result = result - 5
    except:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "매출액에 공백이 있어 분석할 수 없습니다."      
      analysis = analysis  + "</td></tr>"

    #당기손이익
    try:
      if(float(dict_list[2][2][0]) < 0):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "최근년도에 적자를 기록한 기업입니다."      
        analysis = analysis  + "</td></tr>"
        result = result - 100
      elif(float(dict_list[2][0][0]) < float(dict_list[2][1][0]) and float(dict_list[2][1][0]) < float(dict_list[2][2][0])):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "당기손이익이 최근3년간 증가하고 있는 기업입니다."
        analysis = analysis  + "</td></tr>"
        result = result + 20
      elif(float(dict_list[2][0][0]) > float(dict_list[2][1][0]) and float(dict_list[2][1][0]) > float(dict_list[2][2][0])):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "당기손이익이 최근3년간 감소하고 있는 기업입니다."
        analysis = analysis  + "</td></tr>"
        result = result - 20
      else:
        result = result - 10
    except:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "당기손이익에 공백이 있어 분석할 수 없습니다."
      analysis = analysis  + "</td></tr>"

    #부채비율 : 기업의 자기자본에 대한 부채의 상대적 크기로 기업의 재무위험을 나타내는 지표입니다. 100%이하 안정적 400%이상 조심 600%이상 위험 **은행,금융관련주들은 부채비율무시
    try:
      if(float(dict_list[6][2][0])<100):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "부채비율이 안정적인 기업입니다."
        analysis = analysis  + "</td></tr>"
      elif(float(dict_list[6][2][0])>400):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "부채비율을 조심해야할 기업입니다."       
        analysis = analysis  + "</td></tr>"
      elif(float(dict_list[6][2][0])>600):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "부채비율이 위험한 기업입니다. *금융,은행관련주들은 제외"
        analysis = analysis  + "</td></tr>"
        
    except:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "부채비율에 공백이 있어 분석할 수 없습니다."
      analysis = analysis  + "</td></tr>"

    #당좌비율 : 유동자산 중 가장 짧은 기간에 현금화가 가능한 당좌자산과 유동부채의 규모를 비교함으로써 기업의 단기지급능력을 나타내는 지표입니다.
    try:
      if(float(dict_list[7][2][0]) > 100):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "기업의 단기지급능력(당좌비율)이 안정적입니다."
        analysis = analysis  + "</td></tr>"
    except:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "당좌비율에 공백이 있어 분석할 수 없습니다."
      analysis = analysis  + "</td></tr>"
      

    #유보율 : 기업이 동원할 수 있는 자금량을 측정하는 지표로, 이것이 높을수록 불황에 대한 적응력과 기업의 안전성이 높음. (자본 잉여금+이익 잉여금)/(납입 자본금) * 100
    try:
      if(float(dict_list[8][2][0]) > 100):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "불황에 대한 적응력과 안전성(유보율)이 높은 기업입니다."
        analysis = analysis  + "</td></tr>"
    except:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "유보율에 공백이 있어 분석할 수 없습니다."
      analysis = analysis  + "</td></tr>"

    #PER = 순이익대비 주가가 얼마나 고평가 되었는지 나타내는 지표  (시가총액 / 당기순이익)
    try:
      if(float(dict_list[10][2][0]) > 10):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "순이익대비주가(PER)가 고평가 되었습니다."
        analysis = analysis  + "</td></tr>"
    except:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "PER에 공백이 있어 분석할 수 없습니다."
      analysis = analysis  + "</td></tr>"
      

    current_price=market_info[3].get_text().split()[1].replace(",","")
    #BPS : 기업이 지금당장 모든 활동을 중당하고 기업의 자산을 주주들에게 나눠줄 경우, 한 주당 얼마씩 돌아가는지를 나타내는 지표(기업 순자산/발행주식수)
    try:
      if(float(dict_list[11][2][0]) > float(current_price)):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "현재 발행된 주식자산보다 기업순자산이 더 많습니다."
        analysis = analysis  + "</td></tr>"
      else:
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "기업순자산보다 현재 발행된 주식자산 더 많습니다."
        analysis = analysis  + "</td></tr>"
        
    except:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "BPS에 공백이 있어 분석할 수 없습니다."
      analysis = analysis  + "</td></tr>"


    #PBR = 기업자본 대비 주가가 얼마나 고평가 되었는지 나타내는 지표 PBR이 1이하이면 자본대비 저평가, 1이상이면 자본대비 고평가 (시가총액/ 자본총액)
    try:
      if(float(dict_list[12][2][0]) <= 1):
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "자본대비 저평가된 기업입니다."
        analysis = analysis  + "</td></tr>"
      else:
        analysis = analysis  + "<tr><td>"
        analysis = analysis + "자본대비 고평가된 기업입니다."
        analysis = analysis  + "</td></tr>"
    except:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "PBR에 공백이 있어 분석할 수 없습니다."
      analysis = analysis  + "</td></tr>"

    if result > 0:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "매수 선호"
      analysis = analysis  + "</td></tr>"
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "투자에 관한 책임은 투자자에게 있으며 이유없는 매수는 손실을 가져올 수 있습니다."
      analysis = analysis  + "</td></tr>"
      analysis = analysis  + "<tr><td>"
      analysis = analysis  +"현금흐름표 등 추가적인 재무제표분석과 정밀분석을 통해 매수를 결정하시길 바랍니다."
      analysis = analysis  + "</td></tr>"
    else:
      analysis = analysis  + "<tr><td>"
      analysis = analysis + "매수 비선호"
      analysis = analysis  + "</td></tr>"
    
    analysis = analysis + "</table>"
    return result , analysis


def explain(dict_list):
  if dict_list == 0 : #에러가 발생한경우 dict_list =0
    return 0

  explain_text ="""
  <details>
  <summary>용어 설명</summary><p>
  <table>    
        <tr>
            <td>ROE</td>
            <td>기업이 자본을 이용하여 얼마만큼의 이익을 냈는지를 나타내는 지표</td>
        </tr>
        <tr>
            <td>부채비율</td>
            <td>기업의 자기자본에 대한 부채의 상대적 크기로 기업의 재무위험을 나타내는 지표</td>
        </tr>
        <tr>
            <td>당좌비율</td>
            <td>유동자산 중 가장 짧은 기간에 현금화가 가능한 당좌자산과 유동부채의 규모를 비교함으로써 기업의 단기지급능력을 나타내는 지표</td>
        </tr>
        <tr>
            <td>유보율</td>
            <td>기업이 동원할 수 있는 자금량을 측정하는 지표로, 이것이 높을수록 불황에 대한 적응력과 기업의 안전성이 높음</td>
        </tr>
        <tr>
            <td>EPS</td>
            <td>주당순이익</td>
        </tr>
        <tr>
            <td>PER</td>
            <td>순이익대비 주가가 얼마나 고평가 되었는지 나타내는 지표</td>
        </tr>
        <tr>
            <td>BPS</td>
            <td>기업이 지금당장 모든 활동을 중당하고 기업의 자산을 주주들에게 나눠줄 경우, 한 주당 얼마씩 돌아가는지를 나타내는 지표</td>
        </tr>
        <tr>
            <td>PBR</td>
            <td>기업자본 대비 주가가 얼마나 고평가 되었는지 나타내는 지표 PBR이 1이하이면 자본대비 저평가, 1이상이면 자본대비 고평가</td>
        </tr>
        
    </table>    
    </p>
    </details>
    """
                    
  return explain_text


def get_stocks(): # 골든 크로스 종목을 가져옵니다.
  URL = "https://finance.naver.com/sise/item_gold.nhn"
  golden_crossed_stocks_url = requests.get(URL)
  html = golden_crossed_stocks_url.text    
  soup = BeautifulSoup(html, 'lxml')    
  soup = soup.find_all("a","tltle")
  data = []
  for i in range(0,len(soup)):
    data.append(soup[i].get_text())
  return data
def start_analysis(stock):
    positive_golden_crossed_stocks_list = []
    changed_stock = change_stock_to_code(stock)    
    if changed_stock == 0 : #올바르지않은 종목명을 검색하였거나 ,종목코드가없는 코스피200, wti 등을 검색한 경우
      print(changed_stock)
    else: # 재무제표가 없는 선물주식등은 분석이 불가능 ("기업실적분석" 이라는 string의 유무로 재무제표의 유무를 판단가능)            
            _,_,dict_list,market_info,_=crawling(changed_stock)                                
            result,_ =Financial_analysis(dict_list,market_info)
            if result > 0:
                positive_golden_crossed_stocks_list.append(market_info[1].get_text())
            else:
              print()
              #positive_golden_crossed_stocks_list.append("골든크로스 종목인 '"+stock +"'은(는) 당기순이익이 증가하지 않습니다.")
    return positive_golden_crossed_stocks_list

application = app = Flask(__name__)

@app.route('/')
def template_index():    
    return render_template('index.html')

@app.route('/analysis.html' ,methods=["POST","GET"])
def template_analysis():        
    input_text = request.form.get('get_text')    
    stock_code=change_stock_to_code(input_text)
    if stock_code == "해당 증권정보는 종목코드가 없습니다." or stock_code == "올바르지 않은 종목명 입니다." or stock_code == "입력값이 없습니다.":
        return render_template('analysis.html',get_analysis=stock_code)
    #return값 5가지 경우 "해당 증권정보는 종목코드가 없습니다." ,"올바르지 않은 종목명 입니다.","입력값이 없습니다.", 종목코드 , html table string
    elif stock_code.isdigit() == False:  
      return render_template('analysis.html',get_analysis=stock_code)
    else:
        info,summary,dict_list,market_info,Financial_Statements=crawling(stock_code)
        result,analysis = Financial_analysis(dict_list,market_info)
        explain_text=explain(dict_list)
        
        try:
            data="<details><summary>재무제표</summary><p>"
            data=data + Financial_Statements.to_html()
            data= data + "</p></details>"
            
            return render_template('analysis.html',get_info=info,get_summary=summary,data=data,get_analysis=analysis,get_explain=explain_text)
        except:
            if Financial_Statements == 0:
                analysis = "재무제표가 없어서 분석할 수 없습니다.<br>"
            if Financial_Statements == 1:
                analysis = "재무제표 데이터가 적어서 분석을 종료합니다.<br>"
            if Financial_Statements == 2:                
                analysis = "종목코드를 잘못 입력했습니다.<br>"
            explain_text = ""
            return render_template('analysis.html',get_info=info,get_summary=summary,get_analysis=analysis,get_explain=explain_text)



@app.route('/golden_cross.html')
def template_golden_corss():
  f=open('Enterprise.txt','r',encoding='UTF-8')
  fileread = f.read()
  f.close()    
  return render_template('golden_cross.html',get_list=fileread)

@app.route('/Investment_Status.html')
def template_investment_Status():
    return render_template('Investment_Status.html')

@app.route('/memory_test.html') #크롤링 메모리 부하 테스트를 위한 페이지
def memory_test():
    input_text = "삼성증권"
    stock_code=change_stock_to_code(input_text)
    if stock_code == "해당 증권정보는 종목코드가 없습니다." or stock_code == "올바르지 않은 종목명 입니다." or stock_code == "입력값이 없습니다.":
        return render_template('memory_test.html',get_analysis=stock_code)
    #return값 5가지 경우 "해당 증권정보는 종목코드가 없습니다." ,"올바르지 않은 종목명 입니다.","입력값이 없습니다.", 종목코드 , html table string
    elif stock_code.isdigit() == False:      
      return render_template('memory_test.html',get_analysis=stock_code)
    else:
        info,summary,dict_list,market_info,Financial_Statements=crawling(stock_code)
        result,analysis = Financial_analysis(dict_list,market_info)
        explain_text=explain(dict_list)
        
        try:
            data="<details><summary>재무제표</summary><p>"
            data=data + Financial_Statements.to_html()
            data= data + "</p></details>"            
            return render_template('memory_test.html',get_info=info,get_summary=summary,data=data,get_analysis=analysis,get_explain=explain_text)
        except:
            if Financial_Statements == 0:
                analysis = "재무제표가 없어서 분석할 수 없습니다.<br>"
            if Financial_Statements == 1:
                analysis = "재무제표 데이터가 적어서 분석을 종료합니다.<br>"
            if Financial_Statements == 2:                
                analysis = "종목코드를 잘못 입력했습니다.<br>"
            explain_text = ""
            return render_template('memory_test.html',get_info=info,get_summary=summary,get_analysis=analysis,get_explain=explain_text)


@app.route('/memory_test2.html') #크롤링 메모리 부하 테스트를 위한 페이지
def memory_test2():
    input_text = "KO"
    stock_code=change_stock_to_code(input_text)
    print(stock_code)
    if stock_code == "해당 증권정보는 종목코드가 없습니다." or stock_code == "올바르지 않은 종목명 입니다." or stock_code == "입력값이 없습니다.":
        return render_template('memory_test2.html',get_analysis=stock_code)
    #return값 5가지 경우 "해당 증권정보는 종목코드가 없습니다." ,"올바르지 않은 종목명 입니다.","입력값이 없습니다.", 종목코드 , html table string
    elif stock_code.isdigit() == False:      
      return render_template('memory_test2.html',get_analysis=stock_code)
    else:
        info,summary,dict_list,market_info,Financial_Statements=crawling(stock_code)
        result,analysis = Financial_analysis(dict_list,market_info)
        explain_text=explain(dict_list)
        
        try:
            data="<details><summary>재무제표</summary><p>"
            data=data + Financial_Statements.to_html()
            data= data + "</p></details>"            
            return render_template('memory_test2.html',get_info=info,get_summary=summary,data=data,get_analysis=analysis,get_explain=explain_text)
        except:
            if Financial_Statements == 0:
                analysis = "재무제표가 없어서 분석할 수 없습니다.<br>"
            if Financial_Statements == 1:
                analysis = "재무제표 데이터가 적어서 분석을 종료합니다.<br>"
            if Financial_Statements == 2:                
                analysis = "종목코드를 잘못 입력했습니다.<br>"
            explain_text = ""
            return render_template('memory_test2.html',get_info=info,get_summary=summary,get_analysis=analysis,get_explain=explain_text)

@app.route('/loaderio-5f78e5d71875115e0f5f21cdc212e0c9.txt') #Loader 사이트의 서버 부하 테스트를 위한 코드
def traffic_test():
  return "loaderio-5f78e5d71875115e0f5f21cdc212e0c9한글지우면다시테스트가능"

@app.route('/robots.txt')
def robots_txt():
  f=open('robots.txt','r')
  fileread = f.read()
  f.close()  
  return fileread

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html')

@app.errorhandler(500)
def web_server_error500(error):
    return "<h1>안녕하세요 Koinvesting을 이용해 주셔서 감사합니다.</h1><h1>사용자의 급격한 증가로 서버가 다운되었습니다</h1><h1>빠르게 고치겠습니다 죄송합니다.</h1>"

@app.errorhandler(503)
def web_server_error503(error):
    return "<h1>안녕하세요 Koinvesting을 이용해 주셔서 감사합니다.</h1><h1>사용자의 급격한 증가로 서버가 다운되었습니다</h1><h1>빠르게 고치겠습니다 죄송합니다.</h1>"


if __name__ == '__main__':
  freeze_support()  
  app.run()
    
    
