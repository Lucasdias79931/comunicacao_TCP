import os 
import sys
import hashlib

hash = hashlib.sha512('lucasdias'.encode())

print(hash.digest())      # → Retorna os bytes do hash (forma binária)
print(hash.hexdigest())  

print(len(hash.digest()))