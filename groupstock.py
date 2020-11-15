import pandas_datareader.data as web
import pandas as pd
import datetime
from datetime import date,timedelta

import matplotlib.pyplot as plt

from yahoo_fin.stock_info import get_data
import yahoo_fin.stock_info as si
import yfinance as yf

from forex_python.converter import CurrencyRates

import math
import webbrowser
from webbrowser import os

class stock:
    def __init__(self, name):
        quote_table = si.get_quote_table(name, dict_result=False)
        open=quote_table.at[12,'value']
        price=quote_table.at[15,'value']
        prePrice=quote_table.at[14,'value']
        pe=quote_table.at[13,'value']
        avgVol=quote_table.at[3,'value']
        vol=quote_table.at[6,'value']

        ticker=yf.Ticker(name)
        info=ticker.info
        mktCap=info['marketCap']
        mktCapNum=mktCap
        mktCap=mktCap/1000000000
        mktCap="{:.1f}".format(mktCap)
        self.mktCap=mktCap+'B'
        symbol=info['symbol']
        self.ave50=info['fiftyDayAverage']
        self.name=info['shortName']
        country=get_dict_item(info,'country')

        employeeRaw=get_dict_item(info,'fullTimeEmployees')
        if employeeRaw is not None:
          employee=format (employeeRaw, ',d')
        else:
          employee='-'

        instHoldPctRaw=get_dict_item(info,'heldPercentInstitutions')
        if instHoldPctRaw is not None:
          instHoldPct="{:.1%}".format(instHoldPctRaw)
        else:
          instHoldPct='-'
        

        fin=si.get_financials(name)
        # fin_bs_q=fin["quarterly_balance_sheet"]
        fin_bs_q=fin["yearly_balance_sheet"]

        fin_bs_q_dates=fin_bs_q.columns.values
        date=fin_bs_q_dates[0]
        dateStr=str(date)
        self.finDate=dateStr[0:10]

        fin_year_y=fin["yearly_balance_sheet"]
        fin_year_dates_y=fin_year_y.columns.values
        date_y=fin_year_dates_y[0]
        dateStr_y=str(date_y)
        self.finDate_y=dateStr_y[0:10]

        sharesOutstandingRaw=get_dict_item(info,'sharesOutstanding')
        sharesOutstanding=number2M_pure(sharesOutstandingRaw)
        
        ## General
        # Total Asset
        totalAssetsRaw,totalAssets = get_dataframe_item(fin_bs_q,'totalAssets',country,date,0)

        # Total Liabilities
        totalLiabRaw,totalLiab = get_dataframe_item(fin_bs_q,'totalLiab',country,date,0)
        totalLiab_pct = addPct(totalLiabRaw, totalLiab, totalAssetsRaw)

        # Total Equity
        totalEquityRaw = totalAssetsRaw - totalLiabRaw
        totalEquity=number2M(totalEquityRaw,country,date)
        totalEquityRaw_pct = addPct(totalEquityRaw, totalEquity, totalAssetsRaw)

        ## ASSET
        # Total Current Assets
        totalCurrentAssetsRaw,totalCurrentAssets = get_dataframe_item(fin_bs_q,'totalCurrentAssets',country,date,0)
        if totalCurrentAssetsRaw is not None:
          pct="{:.1%}".format(totalCurrentAssetsRaw/totalAssetsRaw)
          totalCurrentAssets = totalCurrentAssets + ' (' + pct +')'

        # Cash
        cashRaw,cash = get_dataframe_item(fin_bs_q,'cash',country,date,0)
        cash_pct = addPct(cashRaw, cash, totalCurrentAssetsRaw)

        # Short Term Investment
        shortTermInvestmentsRaw,shortTermInvestments = get_dataframe_item(fin_bs_q,'shortTermInvestments',country,date,0)
        shortTermInvestments_pct = addPct(shortTermInvestmentsRaw, shortTermInvestments, totalCurrentAssetsRaw)

        # Receivables 
        netReceivablesRaw,netReceivables=get_dataframe_item(fin_bs_q,'netReceivables',country,date,0)
        netReceivables_pct = addPct(netReceivablesRaw, netReceivables, totalCurrentAssetsRaw)

        # Inventory
        inventoryRaw,inventory=get_dataframe_item(fin_bs_q,'inventory',country,date,0)
        inventory_pct=addPct(inventoryRaw, inventory, totalCurrentAssetsRaw)

        # Other Current Asset
        otherCurrentAssetsRaw, otherCurrentAssets = get_dataframe_item(fin_bs_q,'otherCurrentAssets',country,date,0)
        otherCurrentAssets_pct = addPct(otherCurrentAssetsRaw, otherCurrentAssets, totalCurrentAssetsRaw)

        # Total Long Term Asset
        totalLongTermAssetRaw = totalAssetsRaw - totalCurrentAssetsRaw
        totalLongTermAsset = number2M(totalLongTermAssetRaw,country,date)
        totalLongTermAsset_pct = addPct(totalLongTermAssetRaw, totalLongTermAsset, totalAssetsRaw)
        
        # Property, Plant, and Equipment
        propertyPlantEquipmentRaw, propertyPlantEquipment = get_dataframe_item(fin_bs_q,'propertyPlantEquipment',country,date,0)
        propertyPlantEquipment_pct = addPct(propertyPlantEquipmentRaw, propertyPlantEquipment, totalLongTermAssetRaw)

        # Long-term Investment
        longTermInvestmentsRaw,longTermInvestments = get_dataframe_item(fin_bs_q,'longTermInvestments',country,date,0)
        longTermInvestments_pct = addPct(longTermInvestmentsRaw, longTermInvestments, totalLongTermAssetRaw)

        # Net Intangible Asset
        netIntangibleAssetsRaw,netIntangibleAssets=get_dataframe_item(fin_bs_q,'intangibleAssets',country,date,0)
        netIntangibleAssets_pct = addPct(netIntangibleAssetsRaw, netIntangibleAssets, totalLongTermAssetRaw)
        
        # Goodwill
        goodWillRaw,goodWill=get_dataframe_item(fin_bs_q,'goodWill',country,date,0)
        goodWill_pct = addPct(goodWillRaw, goodWill, totalLongTermAssetRaw)

        # Intangible Asset
        intangibleAssetsRaw = netIntangibleAssetsRaw + goodWillRaw
        intangibleAssets=number2M(intangibleAssetsRaw,country,date)
        intangibleAssets_pct = addPct(intangibleAssetsRaw, intangibleAssets, totalLongTermAssetRaw)

        # Other Long-term Asset
        otherAssetsRaw, otherAssets = get_dataframe_item(fin_bs_q,'otherAssets',country,date,0)
        otherAssets_pct = addPct(otherAssetsRaw, otherAssets, totalLongTermAssetRaw)

        # Tangible
        tangibleAssetsRaw=totalAssetsRaw-intangibleAssetsRaw
        tangibleAssets=number2M(tangibleAssetsRaw,country,date)
        tangibleAssets_pct = addPct(tangibleAssetsRaw, tangibleAssets, totalAssetsRaw)


        ## LIABILITY

        # Total Current Liabilities
        totalCurrentLiabilitiesRaw, totalCurrentLiabilities = get_dataframe_item(fin_bs_q,'totalCurrentLiabilities',country,date,0)
        totalCurrentLiabilities_pct = addPct(totalCurrentLiabilitiesRaw, totalCurrentLiabilities, totalLiabRaw)
        
        # Account Payable
        accountsPayableRaw, accountsPayable = get_dataframe_item(fin_bs_q,'accountsPayable',country,date,0)
        accountsPayable_pct = addPct(accountsPayableRaw, accountsPayable, totalCurrentLiabilitiesRaw)

        # Other Current Liabilities
        otherCurrentLiabRaw, otherCurrentLiab = get_dataframe_item(fin_bs_q,'otherCurrentLiab',country,date,0)
        otherCurrentLiab_pct = addPct(otherCurrentLiabRaw, otherCurrentLiab, totalCurrentLiabilitiesRaw)

        # Total Long-term Liablities
        totalLongTermLiabRaw = totalLiabRaw - totalCurrentLiabilitiesRaw
        totalLongTermLiab=number2M(totalLongTermLiabRaw,country,date)
        totalLongTermLiab_pct = addPct(totalLongTermLiabRaw, totalLongTermLiab, totalLiabRaw)

        # Long-term Debt
        longTermDebtRaw, longTermDebt = get_dataframe_item(fin_bs_q,'longTermDebt',country,date,0)
        longTermDebt_pct = addPct(longTermDebtRaw, longTermDebt, totalLongTermLiabRaw)

        shortLongTermDebtRaw, shortLongTermDebt = get_dataframe_item(fin_bs_q,'shortLongTermDebt',country,date,0)
        

        ## EQUITY

        # Minority Interest
        minorityInterestRaw,minorityInterest = get_dataframe_item(fin_bs_q,'minorityInterest',country,date,0)
        minorityInterest_pct = addPct(minorityInterestRaw, minorityInterest, totalEquityRaw)

        # Total Shareholder's Equity
        totalShareholderEquityRaw = totalEquityRaw - minorityInterestRaw
        totalShareholderEquity=number2M(totalShareholderEquityRaw,country,date)
        totalShareholderEquity_pct = addPct(totalShareholderEquityRaw, totalShareholderEquity, totalEquityRaw)

        # Common Stock
        commonStockRaw,commonStock=get_dataframe_item(fin_bs_q,'commonStock',country,date,0)

        # Retained Earnings
        retainedEarningsRaw,retainedEarnings=get_dataframe_item(fin_bs_q,'retainedEarnings',country,date,0)

        # Gains Losses Not Affecting Retained Earnings (Treasury Stock)
        treasuryStockRaw,treasuryStock=get_dataframe_item(fin_bs_q,'treasuryStock',country,date,0)

        # Common Stock Equity
        commonStockEquityRaw, commonStockEquity = get_dataframe_item(fin_bs_q,'totalStockholderEquity',country,date,0)
        commonStockEquity_pct = addPct(commonStockEquityRaw, commonStockEquity, totalShareholderEquityRaw)

        # Preferred Stock Equity
        preferredStockEquityRaw = totalShareholderEquityRaw - commonStockEquityRaw
        preferredStockEquity=number2M(preferredStockEquityRaw,country,date)
        preferredStockEquity_pct = addPct(preferredStockEquityRaw, preferredStockEquity, totalShareholderEquityRaw)

        # Book Value
        bookValueRaw = tangibleAssetsRaw - totalLiabRaw
        bookValue = number2M(bookValueRaw,country,date)

        # Common Book Value
        commonBookValueRaw = commonStockEquityRaw - intangibleAssetsRaw
        commonBookValue = number2M(commonBookValueRaw,country,date)

        capitalSurplusRaw,capitalSurplus=get_dataframe_item(fin_bs_q,'capitalSurplus',country,date,0)

        floatSharesRaw=info["floatShares"]
        floatShares=number2M(floatSharesRaw,country,date)
        
        floatSharesPct="{:.1%}".format(floatSharesRaw/sharesOutstandingRaw)
        
        # FUNDAMENTALS
        workingCapitalRaw=totalCurrentAssetsRaw - totalCurrentLiabilitiesRaw
        if (workingCapitalRaw is not None) & (not math.isnan(workingCapitalRaw)):
          workingCapital=number2M(workingCapitalRaw,country,date)

        # Basic Ratios
        currentRatioRaw=totalCurrentAssetsRaw/totalCurrentLiabilitiesRaw
        currentRatio="{:.2f}".format(currentRatioRaw)

        quickRatioRaw=(totalCurrentAssetsRaw-inventoryRaw)/totalCurrentLiabilitiesRaw
        quickRatio="{:.2f}".format(quickRatioRaw)

        deRaw=totalLiabRaw/totalShareholderEquityRaw
        de="{:.2f}".format(deRaw)

        # BVPS
        bvpsRaw=commonStockEquityRaw/sharesOutstandingRaw
        bvps="{:.2f}".format(bvpsRaw)

        tanBvpsRaw=(commonStockEquityRaw - intangibleAssetsRaw)/sharesOutstandingRaw
        tanBvps="{:.2f}".format(tanBvpsRaw)

        ## Income
        in_quart=fin["quarterly_income_statement"]
        netIncomeRaw,netIncome=get_dataframe_item(in_quart,'netIncome',country,date,0)

        # roeRaw=4*netIncomeRaw/((totalStockholderEquityRaw+totalStockholderEquityRawPre1)/2)
        # roe="{:.1%}".format(roeRaw)

        totalRevenueRaw,totalRevenue=get_dataframe_item(in_quart,'totalRevenue',country,date,0)

        # dfsize=in_quart.shape
        # colNum=dfsize[1]
        # if colNum>1:
        #   sum = totalRevenueRaw
        #   for i in range(1,colNum):
        #     tempRaw,temp=get_dataframe_item(in_quart,'totalRevenue',country,date,i)
        #     sum = sum + tempRaw
        #   totalRevenueRawTTM = sum / colNum
        #   totalRevenueTTM=number2M(totalRevenueRawTTM,country,date)

        grossProfitRaw,grossProfit=get_dataframe_item(in_quart,'grossProfit',country,date,0)
        rd_q0Raw,rd_q0=get_dataframe_item(in_quart,'researchDevelopment',country,date,0)

        in_year=fin["yearly_income_statement"]
        rd_y=in_year.loc['researchDevelopment']
        rd_y0=rd_y.iloc[0]
        if rd_y0 is not None:
            rd_y0=convert_currency(rd_y0,country,date)
            rd_y0=int(rd_y0/1000000)
            rd_y0=format (rd_y0, ',d')
            rd_y0=str(rd_y0)+'M'

        BalanceSheetBasic={
          'Symbol':symbol,
          'MktCapNum':[mktCapNum], # Used for data reorder
          'Tot Asset': totalAssets,
          'Tot Liab': totalLiab_pct,
          'Tot Equity': totalEquityRaw_pct
        }
        df_BalanceSheetBasic=pd.DataFrame(BalanceSheetBasic,index=[0])

        d={
            'Symbol':symbol,
            'MktCapNum':mktCapNum, # Used for data reorder
            'Price':[("{:.2f}".format(price))], 
            'EMPL No.':employee,
            'Qtly Date':self.finDate,
            'Annu Date':self.finDate_y,
            'Shares Outsdg': sharesOutstanding
        }
        df_Old=pd.DataFrame(d,index=[0])

        incomeDetail = {
          'Symbol':symbol,
          'MktCapNum':mktCapNum, # Used for data reorder
          'Net Income': netIncome
        }
        df_incomeDetail=pd.DataFrame(incomeDetail,index=[0])

        assetDetail = {
          'Symbol':symbol,
          'MktCapNum':mktCapNum, # Used for data reorder
          'Tot Asset': totalAssets,
          'Total Current / Tot': totalCurrentAssets,
          'Cash / Cr': cash_pct,
          'ShrtT Invest / Cr': shortTermInvestments_pct,
          'Receivables / Cr': netReceivables_pct,
          'Inventory / Cr':inventory_pct,
          'Other Curr Asset / Cr':otherCurrentAssets_pct,
          'Total Long-term / Tot': totalLongTermAsset_pct,
          'Property,ect / Lng': propertyPlantEquipment_pct,
          'LongT Invest / Lng': longTermInvestments_pct,
          'Intangible / Lng': intangibleAssets_pct,
          'Net Intangible / Lng': netIntangibleAssets_pct,
          'Goodwill / Lng':goodWill_pct,
          'Other LongT Asset / Lng': otherAssets_pct,
          'Tangible /  Tot':tangibleAssets_pct,
        }
        df_assetDetail=pd.DataFrame(assetDetail,index=[0])

        liabilityDetail = {
          'Symbol':symbol,
          'MktCapNum':mktCapNum, # Used for data reorder
          'Tot Liab': totalLiab,
          'Total Current / Tot': totalCurrentLiabilities_pct,
          'Acc Payable / Cr': accountsPayable_pct,
          'Other Curr / Cr': otherCurrentLiab_pct,
          'Total Long / Tot': totalLongTermLiab_pct,
          'Long Debt / Lng': longTermDebt_pct,
          'shortLongTermDebt': shortLongTermDebt
        }
        df_liabilityDetail=pd.DataFrame(liabilityDetail,index=[0])

        equityDetail = {
          'Symbol':symbol,
          'MktCapNum':mktCapNum, # Used for data reorder
          'Tot Eqty': totalEquity,
          'Mnrty Int / Tot': minorityInterest_pct,
          'Tot Sh Eqty / Tot': totalShareholderEquity_pct, 
          'Commn Eqty / ShH': commonStockEquity_pct,
          'Prffd Eqty / ShH': preferredStockEquity_pct,
          'Book Val': bookValue,
          'Comn Book Val': commonBookValue,
          'Cap Surplus': capitalSurplus
        }
        df_equityDetail=pd.DataFrame(equityDetail,index=[0])

        fundamentals = {
          'Symbol':symbol,
          'MktCapNum':mktCapNum, # Used for data reorder
          'Wrk Cap':workingCapital,
        }
        df_fundamentals=pd.DataFrame(fundamentals,index=[0])

        baiscRatios = {
          'Symbol':symbol,
          'MktCapNum':mktCapNum, # Used for data reorder
          'Current Rt': currentRatio,
          'Quick Rt': quickRatio,
          'Debt-Equity': de,
          'BVPS': bvps,
          'TanBVPS': tanBvps
        }
        df_baiscRatios=pd.DataFrame(baiscRatios,index=[0])

        self.output={
          'General Information': df_Old,
          'Balance Sheet Basic': df_BalanceSheetBasic,
          'Income': df_incomeDetail,
          'Assets Details': df_assetDetail,
          'Liability Details': df_liabilityDetail,
          'Equity Details': df_equityDetail,
          'Fundamentals': df_fundamentals,
          'Basic Ratios': df_baiscRatios
          }

def print_stocks_list(StockLists,htmlName):
  htmlBody=''
  f = open(htmlName, "w")
  for sList in StockLists:
        f.write('<H1>'+sList+'</H1>')
        htmlBody=htmlBody+'<H1>'+sList+'</H1>'
        thisList=StockLists[sList]
        stockNum=len(thisList)
        stockObjects=[]
        for company in thisList:
            stockObjects.append(stock(company))
      # Get first stock information
        outputData=stockObjects[0].output
      
        for subTable in outputData:
            f.write('<H3>'+subTable+'</H3>')
            htmlBody=htmlBody+'<H3>'+subTable+'</H3>'
            df=outputData[subTable]
            if stockNum>1:
                compaylist=[]
                compaylist.append(df)
                for i_stock in range(1,stockNum):
                    otherOutputData=stockObjects[i_stock].output
                    dfNew=otherOutputData[subTable]
                    compaylist.append(dfNew)
                df=pd.concat(compaylist)
            df=df.sort_values(by='MktCapNum',ascending=False)
            df=df.drop(columns='MktCapNum')
            sym=df.iloc[:, lambda df:0]
            symVal=sym.values
            df.index=symVal
            df=df.drop(columns='Symbol')
            s=df.to_html().replace("[bug]","<br />")
            htmlBody=htmlBody+'\n'+s
            f.write(s)
  f.close()
  return htmlBody

def convert_currency(number,country,date64):
  date=datetime.datetime.utcfromtimestamp(date64.tolist()/1e9)
  if country=='United States':
    return number
  else:
    c = CurrencyRates()
    if country=='China':
      return c.convert('CNY', 'USD', number, date)
    elif country=='Japan':
      return c.convert('JPY', 'USD', number, date)
    elif country=='India':
      return c.convert('INR', 'USD', number, date)
    elif country=='Canada':
      return c.convert('CAD', 'USD', number, date)
    elif country=='Germany':
      return c.convert('EUR', 'USD', number, date)
    else:
      return 0

def number2M(number,country,date):
    number=convert_currency(number,country,date)
    number=int(number/1000000)
    number=format (number, ',d')
    number=str(number)+'M'
    return number

def number2M_pure(number):
    number=(number/1000000)
    if number>100:
      number=round(number)
    elif number>10:
      number="{:.1f}".format(number)
    else:
      number="{:.2f}".format(number)
    number=format (number, ',d')
    number=str(number)+'M'
    return number

def get_dataframe_item(theDataFrame,item,country,dateValue,num):
  if item in theDataFrame.index:
    itemValueRaw=theDataFrame.loc[item]
    itemValueRaw=itemValueRaw[num]
    if (itemValueRaw is not None): 
      if (not math.isnan(itemValueRaw)):
        itemValue=number2M(itemValueRaw,country,dateValue)
      else:
        itemValueRaw=0
        itemValue='-'
    else:
      itemValueRaw=0
      itemValue='-'
  else:
    itemValueRaw=0
    itemValue='-'
  return itemValueRaw,itemValue

def get_dict_item(theDict,item):
  if item in theDict:
    employeeRaw=theDict[item]
  else:
    employeeRaw=None
  return employeeRaw

def get_stat_value(st,attStr):
    for i in range(len(st)):
        if st.at[i,'Attribute']==attStr:
            itemValue = st.at[i,'Value']
            itemValueRaw=float(itemValue)
            break
    return itemValueRaw,itemValue

def addPct(dataRaw,data,motherRaw):
  if dataRaw is not None:
    if (dataRaw!=0) & (motherRaw!=0):
      pct="{:.1%}".format(dataRaw/motherRaw)
      newData = data + ' (' + pct +')'
    else:
      newData = data
  else:
    newData = data
  return newData