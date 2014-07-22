Sale documents:

* [Intended use of revenue](https://www.ethereum.org/pdfs/IntendedUseOfRevenue.pdf)
* [ĐΞV plan](https://www.ethereum.org/pdfs/%C4%90%CE%9EVPLAN.pdf)
* [White paper](https://www.ethereum.org/pdfs/EthereumWhitePaper.pdf)
* [Yellow paper](https://www.ethereum.org/pdfs/EthereumYellowPaper.pdf)
* [Terms and conditions](https://www.ethereum.org/pdfs/TermsAndConditionsOfTheEthereumGenesisSale.pdf)
* [Ether Product Purchase Agreement](https://www.ethereum.org/pdfs/EtherProductPurchaseAgreement.pdf)

Notes:

1. Purchase minimum is 0.01 BTC
2. Soft purchase maximum is 3000000000 ETH; this script enforces 1500 BTC. If your purchase is larger, contact largepurchases@ethereum.org
3. Please don't try to purchase ether directly into a contract address that you intend to create post-genesis. We know that at least some of you are clever enough to try this, but we take no responsibility for what happens when we change the protocol or the way that contract addresses are generated. Additionally, right now contract addresses depend on sender address and nonce only, so you're not really getting any extra security.
4. Be sure not to lose your wallet or your password. Modern psychological understanding of human memory suggests that coming up with a new password in your head and then not using it for the six months before genesis will likely lead to you forgetting the password, so consider writing the password down.
5. DON'T LOSE YOUR WALLET OR YOUR PASSWORD
6. DON'T LOSE YOUR WALLET OR YOUR PASSWORD
7. DON'T LOSE YOUR WALLET OR YOUR PASSWORD

Instructions:

1. `python pyethsaletool.py genwallet`, enter a password and email
2. Make sure you write down the password or otherwise keep it safe, and make sure you backup your wallet file (saved at ethwallet.json by default, you can use -w to save it somewhere else)
3. Send BTC into the intermediate address provided
4. Use `python pyethsaletool.py finalize` to send the BTC from the intermediate address to the exodus

Alternative cold wallet setup:

1. Install pyethereum on a cold wallet device
2. Use `cat /dev/urandom | head -c 1000 | pyethtool -b sha3 > priv.key` on the CWD to make a private key
3. `cat priv.key | pyethtool -s privtoaddr` to get your address
4. Copy the address to an online laptop, and switch to the laptop for the remaining steps
5. `python pyethsaletool.py genwallet`, enter a password and email
6. Make sure you write down the password or otherwise keep it safe, and make sure you backup your wallet file (saved at ethwallet.json by default, you can use -w to save it somewhere else)
7. Send BTC into the intermediate address provided
8. `python pyethsaletool.py finalize <addr>`, substituting `<addr>` with the address generated on the CWD

Additional instructions:

* To recover the private key of your BTC intermediate address, use `python pyethsaletool.py getbtcprivkey`
* To show your BTC intermediate address, use `python pyethsaletool.py getbtcaddress`
* To recover your ETH privkey, use `python pyethsaletool.py getethprivkey`
* To show your ETH address, use `python pyethsaletool.py getethaddress`
* Use `-w /path/to/wallet.json` if you want to point to a specific wallet file or save your wallet at a specific location
