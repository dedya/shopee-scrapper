import requests
import csv
import time
import random
from os import path
import os

shopId = 9011098
limit=30
 
def product_detail(shopId,itemid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://shopee.co.id/lisuinstrument',
    }   
    url = ("https://shopee.co.id/api/v2/item/get?itemid={}&shopid={}").format(itemid,shopId)
    print(url)
    return requests.get(url,headers=headers).json()

def product_variations(shopId,itemId,modelid):
    url = ("https://shopee.co.id/api/v4/product/get_purchase_quantities_for_selected_model?itemId={}&modelId={}&quantity=1&shopId={}").format(itemId,modelid,shopId)
    return requests.get(url).json()
    
def getShopDetail(shopname):
    url =("https://shopee.co.id/api/v4/shop/get_shop_detail?username={}").format(shopname)
    return requests.get(url).json()

def get_products(shopId,page):
    newest = page*limit
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://shopee.co.id/lisuinstrument',
    }   
    url = ("https://shopee.co.id/api/v2/search_items/?by=sales&limit={}&match_id={}&newest={}&order=desc&page_type=shop&version=2").format(limit,shopId,newest)
    print(url)
    return requests.get(url,headers=headers).json()

def writeCSV(data):
    with open("data.csv", "a",newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        for line in data:
            print(line)
            writer.writerow(line)

def download_image(imageName,itemName,counter=0):
    #name the file so we'll easily find the image
    if counter > 0:
        newFileName = itemName.replace(" ","_").replace("*","_")+"_"+str(counter)+".jpg"
    else:
        newFileName = itemName.replace(" ","_").replace("*","_")+".jpg"
 
    #download if file not exists
    if not path.exists("images/"+newFileName):
        response = requests.get("https://cf.shopee.co.id/file/"+imageName)
        with open("images/"+newFileName, "wb") as file:
            file.write(response.content)
    return newFileName    
    
if __name__ == "__main__":
    toko = input("Masukkan nama toko : ")
    
    try:
        tokoDetail = getShopDetail(toko)
        shopId = tokoDetail['data']['shopid']
        
        #Create image folder if not exists
        if not path.exists('images'):
            os.makedirs('images')

        with open("data.csv", "a",newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            #write header
            header = ['product name','variation name','price','stock','description','images']
            writer.writerow(header)

            #loop for how many page
            for i in range(1,2):
                
                ##get product per page
                products = get_products(shopId,i)
                for j, item in enumerate(products['items'],start=1):
                    #delay random 2-5 seconds
                    time.sleep(random.randrange(2,5))

                    ##get product detail
                    detail = product_detail(shopId,item['itemid'])
                    models = detail['item']['models']

                    for model in models :
                        price = model['price']//10000

                        #get only stock > 0
                        if model['normal_stock'] > 0 :
                            rowData = [item['name'],model['name'],price,model['normal_stock'],detail['item']['description'].encode('utf8')]

                            #get multiple product image
                            if len(item['images']) > 1 :
                                for k, image in enumerate(item['images'],start=1):
                                    newFileName = download_image(image,item['name'],k)
                                    rowData.append(newFileName)
                            else:
                                newFileName = download_image(item['images'][0],item['name'])
                                rowData.append(newFileName)
                            writer.writerow(rowData)
                            print("ada model : "+item['name']+' '+model['name']+' : '+str(model['price']//10000)+';'+str(model['normal_stock']))
    except:
        print("invalid shopname")

   