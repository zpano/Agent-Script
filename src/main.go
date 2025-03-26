package main

import (
    "log"
    "math/big"
    "fmt"

    "github.com/ethereum/go-ethereum/accounts/abi/bind"
    "github.com/ethereum/go-ethereum/common"
    "github.com/ethereum/go-ethereum/crypto"
    "github.com/ethereum/go-ethereum/ethclient"
    "os"
    "agent-script/api"

)

const (
    privateKey = "80e5ac60358518f461a34034055606f0287ae89c96d1db3acfd762f90474fe81"
    zkdcAddress = "0x78376F00F9d61Cd99D62e1B8db34Ffe22e23937d"
    chainid = 0x40d8
)

func main() {
    client, err := ethclient.Dial("https://evmrpc-testnet.0g.ai")
    if err  != nil {
        fmt.Println("ethclient.Dial error : ", err)
        os.Exit(0)
    }

    privateKeyECDSA, err := crypto.HexToECDSA(privateKey)
    if err != nil {
        fmt.Println("crypto.HexToECDSA error:", err)
        os.Exit(1)
    }

    // 
    auth, err := bind.NewKeyedTransactorWithChainID(privateKeyECDSA, big.NewInt(chainid))
    if err != nil {
        fmt.Println("NewKeyedTransactorWithChainID error:", err)
        os.Exit(1)
    }
    zkdc,err := api.NewZDPc(common.HexToAddress(zkdcAddress), client)
    if err != nil {
        fmt.Println("NewZDPc error : ", err)
        os.Exit(0)
    }
    // tx, err := zkdc.SetAgent(auth, common.HexToAddress("0xb6b5b53Dc43D5d84aa49F058517E3A04574a2c4F"))

    proofA,proofB,proofC := getProof()
    swapper,index,a0e,a1m,gasFee,orderType := getUserdata()
    
    tx, err := zkdc.SwapForward(
        auth,
        proofA,
        proofB,
        proofC,
        swapper,
        index,
        a0e,
        a1m,
        gasFee,
        orderType,
    )
    
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("tx sent: %s\n", tx.Hash().Hex())
    // if err = waitConfirm(context.Background(), client, tx.Hash(), time.Minute*2); err != nil {
    //     log.Fatalf("wait confirmation error, please check the tx by yourself: %s", err)
    //    }
    // log.Printf("tx %s confirmed\n", tx.Hash().Hex())
}

func getUserdata() (common.Address,*big.Int,*big.Int,*big.Int,*big.Int,uint8) {
    //Test data
    swapper := common.HexToAddress("0xb6b5b53Dc43D5d84aa49F058517E3A04574a2c4F")
    index := big.NewInt(0)// 0.0015 ETH
    a0e := new(big.Int).SetInt64(1000000000000000000) // 1 ETH
    a1m := new(big.Int).SetInt64(1500000000000000)    // 0.0015 ETH
    gasFee := new(big.Int).Mul(
        big.NewInt(75),
        new(big.Int).Exp(big.NewInt(10), big.NewInt(13), nil), // 0.00075 ETH
    )
    orderType := uint8(0) // ExactInput

    return swapper,index,a0e,a1m,gasFee,orderType

    
}

func getProof() ([2]*big.Int,[2][2]*big.Int,[2]*big.Int) {
    //Test data
    proofA := [2]*big.Int{}
    proofB := [2][2]*big.Int{}
    proofC := [2]*big.Int{}

    if val, ok := new(big.Int).SetString("04694c7ee2d7d5f486b0701867225d904b12bf64ef4d75e11c547523319d170e", 16); ok {
        proofA[0] = val
    }
    if val, ok := new(big.Int).SetString("2cf83f4ddc33aa4203343c116281d8cd6f6342531dd6af7843ce344bb5a711c2", 16); ok {
        proofA[1] = val
    }

    // ProofB
    if val, ok := new(big.Int).SetString("2ec367aecf8fb8b6f6f10822b8f2f626aabfa621398e137f147483f658091d31", 16); ok {
        proofB[0][0] = val
    }
    if val, ok := new(big.Int).SetString("292fceff7a700d586756d57c8f6ddf050e0497b47b9d2e7a3179b6d42425000a", 16); ok {
        proofB[0][1] = val
    }
    if val, ok := new(big.Int).SetString("17df5f1b40fbd5004e2307095102ffe4d0ce0e2ef10fd2bd1dbe9a797bfc11e3", 16); ok {
        proofB[1][0] = val
    }
    if val, ok := new(big.Int).SetString("169a8d10d7d826e98ff8d9166c5c627a2ea64b4f70afec635e57f87123983492", 16); ok {
        proofB[1][1] = val
    }

    // ProofC
    if val, ok := new(big.Int).SetString("21add50213c1894a819c8c5854da0e3948a49512ed7815c793ff8772de675886", 16); ok {
        proofC[0] = val
    }
    if val, ok := new(big.Int).SetString("0f681e2576f40c464c93a038bee85213baf1d149d2691aa3519589e8db53db4e", 16); ok {
        proofC[1] = val
    }
    return proofA,proofB,proofC
}
