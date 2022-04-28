import threading
import time
from socket import *
from threading import *
from tkinter import *

# INIT


lockFileBien = Lock()
lockFileHisto = Lock()
lockFileFact = Lock()

server = socket(AF_INET, SOCK_STREAM)
host = '192.168.1.102'  # gethostbyname(gethostname()) '192.168.1.102'
port = 4839
ADDR = (host, port)
server.bind(ADDR)


def recv_request(conn):
    data = conn.recv(1024).decode('ascii')
    l = data.split()
    ref = l[0]
    typ = l[1]
    val = int(l[2])
    return ref, typ, val


def transaction(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    ref, typ, val = recv_request(conn)
    print("[DATA OBTENTION]")
    print(ref, typ, val)

    bien = open("files/Bien.txt", "r+")

    lockFileBien.acquire()

    liste = []
    print("[SHOW BIEN.TXT]")
    for line in bien.readlines():
        # Getting the values of the line where ref exist
        old_ref, old_val, old_etat, old_plafond = line.split()
        print(old_ref, old_val, old_etat, old_plafond)
        if old_ref == ref:
            liste.append(old_ref)
            liste.append(old_val)
            liste.append(old_etat)
            liste.append(old_plafond)
    print(liste)
    lockFileBien.release()
    bien.close()

    if typ == 'ajout':
        if liste[2] == 'Negatif':
            condition = val - int(liste[1])
            if condition >= 0:

                bien = open("files/Bien.txt", "r")
                lockFileBien.acquire()
                all_lines = bien.readlines()
                index = 0
                for line in all_lines:
                    # Ref must be exactly with 4 letters
                    if line[0] + line[1] + line[2] + line[3] == liste[0]:
                        all_lines[index] = liste[0] + "        " + str(
                            abs(condition)) + "        " + 'Positif' + "        " + liste[
                                               3] + '\n'
                    index = index + 1
                lockFileBien.release()
                bien.close()
                # Rewrite Bien.txt with the new value
                bien = open("files/Bien.txt", "w")
                lockFileBien.acquire()
                bien.writelines(all_lines)
                lockFileBien.release()
                bien.close()

                histo = open("files/histo.txt", "a+")
                lockFileHisto.acquire()
                ligne_histo = liste[0] + "        " + "ajout" + "        " + str(
                    val) + "        " + "succes" + "        " + liste[2]
                histo.write("\n" + str(ligne_histo))
                lockFileHisto.release()
                histo.close()

            else:

                bien = open("files/Bien.txt", "r")
                lockFileBien.acquire()
                all_lines = bien.readlines()
                index = 0
                for line in all_lines:
                    if line[0] + line[1] + line[2] + line[3] == liste[0]:
                        all_lines[index] = liste[0] + "        " + str(
                            abs(condition)) + "        " + "Negatif" + "        " + liste[
                                               3] + '\n'

                    index = index + 1
                lockFileBien.release()
                bien.close()

                bien = open("files/Bien.txt", "w")
                lockFileBien.acquire()
                bien.writelines(all_lines)
                lockFileBien.release()
                bien.close()

                histo = open("files/histo.txt", "a+")
                lockFileHisto.acquire()
                ligne_histo = liste[0] + "        " + "ajout" + "       " + str(
                    val) + "        " + "succes" + "        " + "Negatif"
                histo.write("\n" + str(ligne_histo))
                lockFileHisto.release()
                histo.close()
        else:

            liste[1] = str(val + int(liste[1]))

            bien = open("files/Bien.txt", "r")
            lockFileBien.acquire()
            all_lines = bien.readlines()
            index = 0
            for line in all_lines:
                if line[0] + line[1] + line[2] + line[3] == liste[0]:
                    all_lines[index] = liste[0] + "        " + liste[1] + "        " + "Positif" + "        " + liste[3] \
                                       + '\n'

                index = index + 1
            lockFileBien.release()
            bien.close()

            bien = open("files/Bien.txt", "w")
            lockFileBien.acquire()
            bien.writelines(all_lines)
            lockFileBien.release()
            bien.close()

            histo = open("files/histo.txt", "a+")
            lockFileHisto.acquire()
            ligne_histo = liste[0] + "        " + "ajout" + "        " + str(
                val) + "        " + "succes" + "        " + "Positif"
            histo.write("\n" + str(ligne_histo))
            lockFileHisto.release()
            histo.close()

    if typ == 'retrait':

        if liste[2] == 'Positif':
            # max_retrait = int(liste[1]) + int(liste[3])
            if int(liste[1]) >= val:
                # retrait positif
                liste[1] = str(int(liste[1]) - val)
                resultat = 'succes'

                bien = open("files/Bien.txt", "r")
                lockFileBien.acquire()
                all_lines = bien.readlines()
                index = 0
                for line in all_lines:
                    if line[0] + line[1] + line[2] + line[3] == liste[0]:
                        all_lines[index] = liste[0] + "        " + liste[1] + "        " + "Positif" + "        " + \
                                           liste[
                                               3] + '\n'
                    index = index + 1
                lockFileBien.release()
                bien.close()

                bien = open("files/Bien.txt", "w")
                lockFileBien.acquire()
                bien.writelines(all_lines)
                lockFileBien.release()
                bien.close()

                histo = open("files/histo.txt", "a+")
                lockFileHisto.acquire()

                ligne_histo = liste[0] + "        " + "retrait" + "        " + str(
                    val) + "        " + resultat + "        " + "Positif "
                histo.write("\n" + str(ligne_histo))
                lockFileHisto.release()
                histo.close()

                facture = open("files/facture.txt", "a+")
                lockFileFact.acquire()
                ligne_fact = liste[0] + "        " + "0"
                facture.write(ligne_fact)
                conn.send(ligne_fact.encode('ascii'))
                time.sleep(0.05)
                lockFileFact.release()
                facture.close()
            elif not (int(liste[1]) + int(liste[3]) <= val):
                # retrait négatif ( enter rouge)

                nv_solde = abs(int(liste[1]) - val)
                fact = nv_solde * 2 / 100

                bien = open("files/Bien.txt", "r")
                lockFileBien.acquire()
                all_lines = bien.readlines()
                index = 0
                for line in all_lines:
                    if line[0] + line[1] + line[2] + line[3] == liste[0]:
                        all_lines[index] = liste[0] + "        " + str(nv_solde) + "        " + 'Negatif' + "        " + \
                                           liste[3] + '\n'

                    index = index + 1
                lockFileBien.release()
                bien.close()

                bien = open("files/Bien.txt", "w")
                lockFileBien.acquire()
                bien.writelines(all_lines)
                lockFileBien.release()
                bien.close()

                histo = open("files/histo.txt", "a+")
                lockFileHisto.acquire()

                ligne_histo = liste[0] + "        " + "retrait" + "       " + str(
                    val) + "        " + 'succes' + "        " + 'Negatif'
                histo.write("\n" + str(ligne_histo))
                lockFileHisto.release()
                histo.close()

                facture = open("files/facture.txt", "a+")
                lockFileFact.acquire()

                ligne_fact = liste[0] + "        " + str(fact)
                facture.write("\n" + str(ligne_fact))
                conn.send(ligne_fact.encode('ascii'))
                time.sleep(0.05)
                lockFileFact.release()
                facture.close()

            else:
                # limite rouge dépassé

                histo = open("files/histo.txt", "a+")
                lockFileHisto.acquire()
                ligne_histo = liste[0] + "        " + "retrait" + "        " + str(
                    val) + "        " + 'echec' + "        " + "Negatif"
                histo.write("\n" + str(ligne_histo))
                lockFileHisto.release()
                histo.close()

        else:
            if (int(liste[3]) - int(liste[1])) >= val:
                # retrait rouge

                nv_solde = val + int(liste[1])
                fact = val * 2 / 100

                bien = open("files/Bien.txt", "r")
                lockFileBien.acquire()
                all_lines = bien.readlines()
                index = 0
                for line in all_lines:
                    if line[0] + line[1] + line[2] + line[3] == liste[0]:
                        all_lines[index] = liste[0] + "        " + str(nv_solde) + "        " + "Negatif" + "        " + \
                                           liste[3] + '\n'

                    index = index + 1
                lockFileBien.release()
                bien.close()

                bien = open("files/Bien.txt", "w")
                lockFileBien.acquire()
                bien.writelines(all_lines)
                lockFileBien.release()
                bien.close()

                histo = open("files/histo.txt", "a+")
                lockFileHisto.acquire()

                ligne_histo = liste[0] + "        " + "retrait" + "        " + str(
                    val) + "       " + 'succes' + "        " + "Negatif"
                histo.write("\n" + str(ligne_histo))
                lockFileHisto.release()
                histo.close()

                facture = open("files/facture.txt", "a+")
                lockFileFact.acquire()

                ligne_fact = liste[0] + "        " + str(fact)
                facture.write("\n" + str(ligne_fact))
                conn.send(ligne_fact.encode('ascii'))
                time.sleep(0.05)
                lockFileFact.release()
                facture.close()

            else:
                # limite rouge dépassé

                histo = open("files/histo.txt", "a+")
                lockFileHisto.acquire()
                ligne_histo = liste[0] + "        " + "retrait" + "        " + str(
                    val) + "        " + 'echec' + "        " + "Negatif"
                histo.write("\n" + str(ligne_histo))
                lockFileHisto.release()
                histo.close()


def consult_client(ref):
    print("Consulting the client with the reference : " + ref)
    bien = open("files/Bien.txt", "r")
    all_lines = bien.readlines()
    index = 0
    for line in all_lines:
        if line[0] + line[1] + line[2] + line[3] == ref:
            print(all_lines[index])
        index = index + 1
    bien.close()
    return 0


def consult_facture_account(ref):
    print("Consulting receipt of the client with the reference : " + ref)
    fact = open("files/facture.txt", "r")
    all_lines = fact.readlines()
    index = 0
    for line in all_lines:
        if line[0] + line[1] + line[2] + line[3] == ref:
            print(all_lines[index])
        index = index + 1
    fact.close()
    return 0


def consult_historic_transactions():
    print("Transaction historic :")
    histo = open("files/histo.txt", "r")
    all_lines = histo.readlines()
    for line in all_lines:
        print(line)
    histo.close()
    return 0


def start():
    while True:
        conn, addr = server.accept()
        thread = Thread(target=transaction, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    server.listen()
    print("[STARTING] Server is starting...")
    print("Waiting for connection ...")
    ACCEPT_THREAD = Thread(target=start)
    ACCEPT_THREAD.start()
    consult_client("2000")
    consult_facture_account("2000")
    consult_historic_transactions()
    ACCEPT_THREAD.join()
    server.close()
