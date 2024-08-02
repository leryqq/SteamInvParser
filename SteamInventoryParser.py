import requests
import json
import os

STEAM_ID = input('Account Steam ID64: ')
GAME_ID = input('Game ID: ')
CURRENCY = '2'
LANGUAGE = 'english'
ITEMS_PER_REQUEST = '2000' #defaul step value = 2000
LAST_ASSET_ID = '0'
TOTAL_INV_COUNT = 0


GET_INV_DATA_URL = 'https://steamcommunity.com/inventory/'+ STEAM_ID + '/' + GAME_ID + '/' + CURRENCY + '?l=' + LANGUAGE + '&count=' + ITEMS_PER_REQUEST + '&start_assetid=' + LAST_ASSET_ID

ITEM_DATA_COUNT = []

itemsChecked = 0

try:
    response = requests.get(GET_INV_DATA_URL)
    response.raise_for_status()
    inventoryData = json.loads(response.text)
    print(f'Data get successfully')
    assets = inventoryData['assets']
    descriptions = inventoryData['descriptions']
    TOTAL_INV_COUNT = inventoryData['total_inventory_count']

    while TOTAL_INV_COUNT > itemsChecked:
        
        response = requests.get('https://steamcommunity.com/inventory/'+ STEAM_ID + '/' + GAME_ID + '/' + CURRENCY + '?l=' + LANGUAGE + '&count=' + ITEMS_PER_REQUEST + '&start_assetid=' + LAST_ASSET_ID)
        response.raise_for_status()
        inventoryData = json.loads(response.text)
        
        assets = inventoryData['assets']
        descriptions = inventoryData['descriptions']
        if 'last_assetid' in inventoryData:
            LAST_ASSET_ID = inventoryData['last_assetid']
        print(f'Items checked: ' + str(len(assets) + itemsChecked))
        itemsChecked += len(assets)

        for asset in assets:
            assetClassId = asset['classid']
            for description in descriptions:
                descriptionClassId = description['classid']
                if assetClassId == descriptionClassId:
                    counter = 0
                    if len(ITEM_DATA_COUNT) != 0:
                            if assetClassId in [item['id'] for item in ITEM_DATA_COUNT]:
                                for itemDataCount in ITEM_DATA_COUNT:
                                    if assetClassId == itemDataCount['id']:
                                        counter +=1
                                        itemDataCount['quantity'] = int(itemDataCount['quantity']) + 1
                        
                            else:
                                itemToSave = {
                                    "id": assetClassId,
                                    "icon_url": description['icon_url'],
                                    "name": description['name'],
                                    "quantity": 1,
                                    "type": description['type'],
                                    "market_name": description['market_name'],
                                    "market_hash_name": description['market_hash_name']
                                }
                                ITEM_DATA_COUNT.append(itemToSave)
                            
                    else:
                        itemToSave = {
                            "id": assetClassId,
                            "icon_url": description['icon_url'],
                            "name": description['name'],
                            "quantity": 1,
                            "type": description['type'],
                            "market_name": description['market_name'],
                            "market_hash_name": description['market_hash_name']
                        }
                        ITEM_DATA_COUNT.append(itemToSave)

    if not os.path.exists('inventory_data'):
        os.makedirs('inventory_data')

    with open(os.path.join('inventory_data', STEAM_ID + '_items.json'), 'w', encoding='utf-8') as f:
        json.dump(ITEM_DATA_COUNT, f, ensure_ascii=False, indent=4)

    print('Data successfully saved!')

except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error: {http_err}")