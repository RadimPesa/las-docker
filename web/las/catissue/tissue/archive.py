import optparse, os, sys
#from openpyxl.reader.excel import load_workbook
import xlrd,xlwt

def main():
	#carico il file degli espianti
	f1 = open('Explants.csv')
	espianti = f1.readlines()
	f1.close()
	dizio={}
	for espi in espianti:
		val_esp=espi.split(';')
		id_esp=val_esp[0]
		gen_esp=val_esp[2]
		dizio[id_esp]=gen_esp
	leggi= xlrd.open_workbook("DTB_ArchiveTissues_OK.xls") 
	scrivi = xlwt.Workbook(encoding="utf-8")
 
	sheet = leggi.sheet_by_name('ArchiveSeries') 
	sh=scrivi.add_sheet('ArchiveSeries') 
	for i in range (0,sheet.nrows):
		for j in range(0,sheet.ncols):
			sh.write(i,j,sheet.row_values(i)[j])

   	sheet = leggi.sheet_by_name('Archive Specifications') 
	sh=scrivi.add_sheet('Archive Specifications') 
	print sheet.nrows
	for i in range (0,sheet.nrows):
		for j in range(0,sheet.ncols):
			#e' la colonna dell'id espianto
			if j==4:
				idexpl=sheet.row_values(i)[3]
				if idexpl in dizio:
					gen=dizio[idexpl]
					#confronto il gen con quello che c'e' nel file
					gen_file=sheet.row_values(i)[2]
					if gen!=gen_file:
						#print 'diverso'
						#prendo quello che c'e' nella colonna E
						gen_lungo=sheet.row_values(i)[4]
						gen_nuovo=gen+gen_lungo[-4:]
						sh.write(i,j,gen_nuovo)
						sh.write(i,sheet.ncols,'CHANGE')
					else:
						sh.write(i,j,sheet.row_values(i)[j])
				else:
					sh.write(i,j,sheet.row_values(i)[j])
			else:
				sh.write(i,j,sheet.row_values(i)[j])

	sheet = leggi.sheet_by_name('Sheet3') 
	sh=scrivi.add_sheet('Sheet3') 
	for i in range (0,sheet.nrows):
		for j in range(0,sheet.ncols):
			sh.write(i,j,sheet.row_values(i)[j])


	scrivi.save("Archive_Tissues_2.xls")
	

if __name__=='__main__':
	main()

