"""
Data from SimplePay bulk add Excel sheet that maps a number of constants used
int the API to their string values.

Data derived from https://www.simplepay.co.za/clients/150709/employee_bulk_inputs/excel_export?employee_level=true&type=all

"""

BANKS = {int(l.split()[-1]):' '.join(l.split()[0:-1])
        for l in """
ABSA Bank	1462381520
Capitec Bank	464954524
First National Bank	1809393886
Nedbank	189450181
Standard Bank	284678023
20twenty	1823577098
Access Bank South Africa Limited	946575179
African Bank	2081327577
Albaraka	2081327576
Bank of Transkei	560121584
Bank of Windhoek	1449522790
Bank Zero	2081327609
Bidvest Bank	2081327518
Boland Bank PKS	1208050630
Cape of Good Hope Bank	1057379156
Citibank South Africa	638517993
Commercial Bank of Namibia	1359491711
Discovery Bank	2081327605
Fidelity Bank	1102524399
Finbond Mutual Bank	2081327606
Future Bank Corporation	917512057
Grindrod Bank	2081327607
HBZ Bank	1651121208
HSBC	1229410299
Investec Bank	359476398
Ithala	2081327574
Mercantile Bank	207912213
Natal Building Society	2070105475
Old Mutual	1347296834
People's Bank	1695012897
Permanent Bank	302049463
Pick 'n Pay Go Banking	1044414317
Postbank	2081327517
Rand Merchant Bank	659107544
Saambou Bank	185186574
SASFIN Bank	2081327590
Tyme Digital Bank	2081327592
UBank (formerly Teba Bank)	2081327519
Unibank	2081327516
VBS Mutual Bank	2081327575
""".split('\n')
    if l}   

