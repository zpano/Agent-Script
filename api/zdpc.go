// Code generated - DO NOT EDIT.
// This file is a generated binding and any manual changes will be lost.

package api

import (
	"errors"
	"math/big"
	"strings"

	ethereum "github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/accounts/abi/bind"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/event"
)

// Reference imports to suppress errors if they are not otherwise used.
var (
	_ = errors.New
	_ = big.NewInt
	_ = strings.NewReader
	_ = ethereum.NotFound
	_ = bind.Bind
	_ = common.Big1
	_ = types.BloomLookup
	_ = event.NewSubscription
	_ = abi.ConvertType
)

// ZDPcOrder is an auto generated low-level Go binding around an user-defined struct.
type ZDPcOrder struct {
	T    ZDPcOrderDetails
	HOsF [16]byte
	HOsE [16]byte
}

// ZDPcOrderDetails is an auto generated low-level Go binding around an user-defined struct.
type ZDPcOrderDetails struct {
	Swapper         common.Address
	Recipient       common.Address
	TokenIn         common.Address
	TokenOut        common.Address
	ExchangeRate    *big.Int
	Deadline        *big.Int
	OrderIsExecuted bool
	IsMultiPath     bool
	EncodedPath     []byte
}

// ZDPcMetaData contains all meta data concerning the ZDPc contract.
var ZDPcMetaData = &bind.MetaData{
	ABI: "[{\"type\":\"constructor\",\"inputs\":[{\"name\":\"_agent\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"_router\",\"type\":\"address\",\"internalType\":\"addresspayable\"},{\"name\":\"_verifier\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"_owner\",\"type\":\"address\",\"internalType\":\"address\"}],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"MAX_ACTIVE_ORDER\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"uint256\",\"internalType\":\"uint256\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"acceptOwnership\",\"inputs\":[],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"activeOrders\",\"inputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"\",\"type\":\"uint256\",\"internalType\":\"uint256\"}],\"outputs\":[{\"name\":\"\",\"type\":\"uint256\",\"internalType\":\"uint256\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"addPendingOrder\",\"inputs\":[{\"name\":\"_order\",\"type\":\"tuple\",\"internalType\":\"structZDPc.Order\",\"components\":[{\"name\":\"t\",\"type\":\"tuple\",\"internalType\":\"structZDPc.OrderDetails\",\"components\":[{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"recipient\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"tokenIn\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"tokenOut\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"exchangeRate\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"deadline\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"OrderIsExecuted\",\"type\":\"bool\",\"internalType\":\"bool\"},{\"name\":\"isMultiPath\",\"type\":\"bool\",\"internalType\":\"bool\"},{\"name\":\"encodedPath\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"HOsF\",\"type\":\"bytes16\",\"internalType\":\"bytes16\"},{\"name\":\"HOsE\",\"type\":\"bytes16\",\"internalType\":\"bytes16\"}]}],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"agent\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"address\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"cancelOrder\",\"inputs\":[{\"name\":\"index\",\"type\":\"uint256\",\"internalType\":\"uint256\"}],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"depositForGasFee\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"}],\"outputs\":[],\"stateMutability\":\"payable\"},{\"type\":\"function\",\"name\":\"gasfee\",\"inputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"address\"}],\"outputs\":[{\"name\":\"\",\"type\":\"uint256\",\"internalType\":\"uint256\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"getActiveOrders\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"}],\"outputs\":[{\"name\":\"\",\"type\":\"uint256[]\",\"internalType\":\"uint256[]\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"getOrder\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"index\",\"type\":\"uint256\",\"internalType\":\"uint256\"}],\"outputs\":[{\"name\":\"\",\"type\":\"tuple\",\"internalType\":\"structZDPc.Order\",\"components\":[{\"name\":\"t\",\"type\":\"tuple\",\"internalType\":\"structZDPc.OrderDetails\",\"components\":[{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"recipient\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"tokenIn\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"tokenOut\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"exchangeRate\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"deadline\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"OrderIsExecuted\",\"type\":\"bool\",\"internalType\":\"bool\"},{\"name\":\"isMultiPath\",\"type\":\"bool\",\"internalType\":\"bool\"},{\"name\":\"encodedPath\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"HOsF\",\"type\":\"bytes16\",\"internalType\":\"bytes16\"},{\"name\":\"HOsE\",\"type\":\"bytes16\",\"internalType\":\"bytes16\"}]}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"getOrders\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"}],\"outputs\":[{\"name\":\"\",\"type\":\"tuple[]\",\"internalType\":\"structZDPc.Order[]\",\"components\":[{\"name\":\"t\",\"type\":\"tuple\",\"internalType\":\"structZDPc.OrderDetails\",\"components\":[{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"recipient\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"tokenIn\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"tokenOut\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"exchangeRate\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"deadline\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"OrderIsExecuted\",\"type\":\"bool\",\"internalType\":\"bool\"},{\"name\":\"isMultiPath\",\"type\":\"bool\",\"internalType\":\"bool\"},{\"name\":\"encodedPath\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"HOsF\",\"type\":\"bytes16\",\"internalType\":\"bytes16\"},{\"name\":\"HOsE\",\"type\":\"bytes16\",\"internalType\":\"bytes16\"}]}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"orderbook\",\"inputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"\",\"type\":\"uint256\",\"internalType\":\"uint256\"}],\"outputs\":[{\"name\":\"t\",\"type\":\"tuple\",\"internalType\":\"structZDPc.OrderDetails\",\"components\":[{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"recipient\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"tokenIn\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"tokenOut\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"exchangeRate\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"deadline\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"OrderIsExecuted\",\"type\":\"bool\",\"internalType\":\"bool\"},{\"name\":\"isMultiPath\",\"type\":\"bool\",\"internalType\":\"bool\"},{\"name\":\"encodedPath\",\"type\":\"bytes\",\"internalType\":\"bytes\"}]},{\"name\":\"HOsF\",\"type\":\"bytes16\",\"internalType\":\"bytes16\"},{\"name\":\"HOsE\",\"type\":\"bytes16\",\"internalType\":\"bytes16\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"owner\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"address\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"pendingOwner\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"address\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"renounceOwnership\",\"inputs\":[],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"router\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractISwapRouter\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"setAgent\",\"inputs\":[{\"name\":\"_agent\",\"type\":\"address\",\"internalType\":\"address\"}],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"setRouter\",\"inputs\":[{\"name\":\"_router\",\"type\":\"address\",\"internalType\":\"address\"}],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"setVerifier\",\"inputs\":[{\"name\":\"_verifier\",\"type\":\"address\",\"internalType\":\"address\"}],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"swapForward\",\"inputs\":[{\"name\":\"_proofA\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"_proofB\",\"type\":\"uint256[2][2]\",\"internalType\":\"uint256[2][2]\"},{\"name\":\"_proofC\",\"type\":\"uint256[2]\",\"internalType\":\"uint256[2]\"},{\"name\":\"swapper\",\"type\":\"address\",\"internalType\":\"address\"},{\"name\":\"index\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"a0e\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"a1m\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"_gasFee\",\"type\":\"uint256\",\"internalType\":\"uint256\"},{\"name\":\"_type\",\"type\":\"uint8\",\"internalType\":\"enumZDPc.OrderType\"}],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"transferOwnership\",\"inputs\":[{\"name\":\"newOwner\",\"type\":\"address\",\"internalType\":\"address\"}],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"verifier\",\"inputs\":[],\"outputs\":[{\"name\":\"\",\"type\":\"address\",\"internalType\":\"contractGroth16Verifier\"}],\"stateMutability\":\"view\"},{\"type\":\"function\",\"name\":\"withdrawGasFee\",\"inputs\":[{\"name\":\"amount\",\"type\":\"uint256\",\"internalType\":\"uint256\"}],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"function\",\"name\":\"withdrawTakenFee\",\"inputs\":[],\"outputs\":[],\"stateMutability\":\"nonpayable\"},{\"type\":\"event\",\"name\":\"AgentChanged\",\"inputs\":[{\"name\":\"oldAgent\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"newAgent\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"FeeDeposit\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"fee\",\"type\":\"uint256\",\"indexed\":true,\"internalType\":\"uint256\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"FeeTaken\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"fee\",\"type\":\"uint256\",\"indexed\":true,\"internalType\":\"uint256\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"FeeWithdrawn\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"fee\",\"type\":\"uint256\",\"indexed\":true,\"internalType\":\"uint256\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"HOS\",\"inputs\":[{\"name\":\"HOsF\",\"type\":\"bytes16\",\"indexed\":true,\"internalType\":\"bytes16\"},{\"name\":\"HOsE\",\"type\":\"bytes16\",\"indexed\":true,\"internalType\":\"bytes16\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"OrderCancelled\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"indexed\":false,\"internalType\":\"address\"},{\"name\":\"index\",\"type\":\"uint256\",\"indexed\":true,\"internalType\":\"uint256\"},{\"name\":\"tokenIn\",\"type\":\"address\",\"indexed\":false,\"internalType\":\"address\"},{\"name\":\"tokenOut\",\"type\":\"address\",\"indexed\":false,\"internalType\":\"address\"},{\"name\":\"exchangeRate\",\"type\":\"uint256\",\"indexed\":false,\"internalType\":\"uint256\"},{\"name\":\"deadline\",\"type\":\"uint256\",\"indexed\":false,\"internalType\":\"uint256\"},{\"name\":\"OrderIsExecuted\",\"type\":\"bool\",\"indexed\":false,\"internalType\":\"bool\"},{\"name\":\"isMultiPath\",\"type\":\"bool\",\"indexed\":false,\"internalType\":\"bool\"},{\"name\":\"encodedPath\",\"type\":\"bytes\",\"indexed\":false,\"internalType\":\"bytes\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"OrderExecuted\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"indexed\":false,\"internalType\":\"address\"},{\"name\":\"index\",\"type\":\"uint256\",\"indexed\":true,\"internalType\":\"uint256\"},{\"name\":\"tokenIn\",\"type\":\"address\",\"indexed\":false,\"internalType\":\"address\"},{\"name\":\"tokenOut\",\"type\":\"address\",\"indexed\":false,\"internalType\":\"address\"},{\"name\":\"exchangeRate\",\"type\":\"uint256\",\"indexed\":false,\"internalType\":\"uint256\"},{\"name\":\"deadline\",\"type\":\"uint256\",\"indexed\":false,\"internalType\":\"uint256\"},{\"name\":\"OrderIsExecuted\",\"type\":\"bool\",\"indexed\":false,\"internalType\":\"bool\"},{\"name\":\"isMultiPath\",\"type\":\"bool\",\"indexed\":false,\"internalType\":\"bool\"},{\"name\":\"encodedPath\",\"type\":\"bytes\",\"indexed\":false,\"internalType\":\"bytes\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"OrderStored\",\"inputs\":[{\"name\":\"swapper\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"index\",\"type\":\"uint256\",\"indexed\":true,\"internalType\":\"uint256\"},{\"name\":\"tokenIn\",\"type\":\"address\",\"indexed\":false,\"internalType\":\"address\"},{\"name\":\"tokenOut\",\"type\":\"address\",\"indexed\":false,\"internalType\":\"address\"},{\"name\":\"exchangeRate\",\"type\":\"uint256\",\"indexed\":false,\"internalType\":\"uint256\"},{\"name\":\"deadline\",\"type\":\"uint256\",\"indexed\":false,\"internalType\":\"uint256\"},{\"name\":\"OrderIsExecuted\",\"type\":\"bool\",\"indexed\":false,\"internalType\":\"bool\"},{\"name\":\"isMultiPath\",\"type\":\"bool\",\"indexed\":false,\"internalType\":\"bool\"},{\"name\":\"encodedPath\",\"type\":\"bytes\",\"indexed\":false,\"internalType\":\"bytes\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"OwnershipTransferStarted\",\"inputs\":[{\"name\":\"previousOwner\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"newOwner\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"OwnershipTransferred\",\"inputs\":[{\"name\":\"previousOwner\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"newOwner\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"RouterChanged\",\"inputs\":[{\"name\":\"oldRouter\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"newRouter\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"TakenFeeWithdrawn\",\"inputs\":[{\"name\":\"owner\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"fee\",\"type\":\"uint256\",\"indexed\":true,\"internalType\":\"uint256\"}],\"anonymous\":false},{\"type\":\"event\",\"name\":\"VerifierChanged\",\"inputs\":[{\"name\":\"oldVerifier\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"},{\"name\":\"newVerifier\",\"type\":\"address\",\"indexed\":true,\"internalType\":\"address\"}],\"anonymous\":false},{\"type\":\"error\",\"name\":\"OwnableInvalidOwner\",\"inputs\":[{\"name\":\"owner\",\"type\":\"address\",\"internalType\":\"address\"}]},{\"type\":\"error\",\"name\":\"OwnableUnauthorizedAccount\",\"inputs\":[{\"name\":\"account\",\"type\":\"address\",\"internalType\":\"address\"}]},{\"type\":\"error\",\"name\":\"ReentrancyGuardReentrantCall\",\"inputs\":[]}]",
}

// ZDPcABI is the input ABI used to generate the binding from.
// Deprecated: Use ZDPcMetaData.ABI instead.
var ZDPcABI = ZDPcMetaData.ABI

// ZDPc is an auto generated Go binding around an Ethereum contract.
type ZDPc struct {
	ZDPcCaller     // Read-only binding to the contract
	ZDPcTransactor // Write-only binding to the contract
	ZDPcFilterer   // Log filterer for contract events
}

// ZDPcCaller is an auto generated read-only Go binding around an Ethereum contract.
type ZDPcCaller struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// ZDPcTransactor is an auto generated write-only Go binding around an Ethereum contract.
type ZDPcTransactor struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// ZDPcFilterer is an auto generated log filtering Go binding around an Ethereum contract events.
type ZDPcFilterer struct {
	contract *bind.BoundContract // Generic contract wrapper for the low level calls
}

// ZDPcSession is an auto generated Go binding around an Ethereum contract,
// with pre-set call and transact options.
type ZDPcSession struct {
	Contract     *ZDPc             // Generic contract binding to set the session for
	CallOpts     bind.CallOpts     // Call options to use throughout this session
	TransactOpts bind.TransactOpts // Transaction auth options to use throughout this session
}

// ZDPcCallerSession is an auto generated read-only Go binding around an Ethereum contract,
// with pre-set call options.
type ZDPcCallerSession struct {
	Contract *ZDPcCaller   // Generic contract caller binding to set the session for
	CallOpts bind.CallOpts // Call options to use throughout this session
}

// ZDPcTransactorSession is an auto generated write-only Go binding around an Ethereum contract,
// with pre-set transact options.
type ZDPcTransactorSession struct {
	Contract     *ZDPcTransactor   // Generic contract transactor binding to set the session for
	TransactOpts bind.TransactOpts // Transaction auth options to use throughout this session
}

// ZDPcRaw is an auto generated low-level Go binding around an Ethereum contract.
type ZDPcRaw struct {
	Contract *ZDPc // Generic contract binding to access the raw methods on
}

// ZDPcCallerRaw is an auto generated low-level read-only Go binding around an Ethereum contract.
type ZDPcCallerRaw struct {
	Contract *ZDPcCaller // Generic read-only contract binding to access the raw methods on
}

// ZDPcTransactorRaw is an auto generated low-level write-only Go binding around an Ethereum contract.
type ZDPcTransactorRaw struct {
	Contract *ZDPcTransactor // Generic write-only contract binding to access the raw methods on
}

// NewZDPc creates a new instance of ZDPc, bound to a specific deployed contract.
func NewZDPc(address common.Address, backend bind.ContractBackend) (*ZDPc, error) {
	contract, err := bindZDPc(address, backend, backend, backend)
	if err != nil {
		return nil, err
	}
	return &ZDPc{ZDPcCaller: ZDPcCaller{contract: contract}, ZDPcTransactor: ZDPcTransactor{contract: contract}, ZDPcFilterer: ZDPcFilterer{contract: contract}}, nil
}

// NewZDPcCaller creates a new read-only instance of ZDPc, bound to a specific deployed contract.
func NewZDPcCaller(address common.Address, caller bind.ContractCaller) (*ZDPcCaller, error) {
	contract, err := bindZDPc(address, caller, nil, nil)
	if err != nil {
		return nil, err
	}
	return &ZDPcCaller{contract: contract}, nil
}

// NewZDPcTransactor creates a new write-only instance of ZDPc, bound to a specific deployed contract.
func NewZDPcTransactor(address common.Address, transactor bind.ContractTransactor) (*ZDPcTransactor, error) {
	contract, err := bindZDPc(address, nil, transactor, nil)
	if err != nil {
		return nil, err
	}
	return &ZDPcTransactor{contract: contract}, nil
}

// NewZDPcFilterer creates a new log filterer instance of ZDPc, bound to a specific deployed contract.
func NewZDPcFilterer(address common.Address, filterer bind.ContractFilterer) (*ZDPcFilterer, error) {
	contract, err := bindZDPc(address, nil, nil, filterer)
	if err != nil {
		return nil, err
	}
	return &ZDPcFilterer{contract: contract}, nil
}

// bindZDPc binds a generic wrapper to an already deployed contract.
func bindZDPc(address common.Address, caller bind.ContractCaller, transactor bind.ContractTransactor, filterer bind.ContractFilterer) (*bind.BoundContract, error) {
	parsed, err := ZDPcMetaData.GetAbi()
	if err != nil {
		return nil, err
	}
	return bind.NewBoundContract(address, *parsed, caller, transactor, filterer), nil
}

// Call invokes the (constant) contract method with params as input values and
// sets the output to result. The result type might be a single field for simple
// returns, a slice of interfaces for anonymous returns and a struct for named
// returns.
func (_ZDPc *ZDPcRaw) Call(opts *bind.CallOpts, result *[]interface{}, method string, params ...interface{}) error {
	return _ZDPc.Contract.ZDPcCaller.contract.Call(opts, result, method, params...)
}

// Transfer initiates a plain transaction to move funds to the contract, calling
// its default method if one is available.
func (_ZDPc *ZDPcRaw) Transfer(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _ZDPc.Contract.ZDPcTransactor.contract.Transfer(opts)
}

// Transact invokes the (paid) contract method with params as input values.
func (_ZDPc *ZDPcRaw) Transact(opts *bind.TransactOpts, method string, params ...interface{}) (*types.Transaction, error) {
	return _ZDPc.Contract.ZDPcTransactor.contract.Transact(opts, method, params...)
}

// Call invokes the (constant) contract method with params as input values and
// sets the output to result. The result type might be a single field for simple
// returns, a slice of interfaces for anonymous returns and a struct for named
// returns.
func (_ZDPc *ZDPcCallerRaw) Call(opts *bind.CallOpts, result *[]interface{}, method string, params ...interface{}) error {
	return _ZDPc.Contract.contract.Call(opts, result, method, params...)
}

// Transfer initiates a plain transaction to move funds to the contract, calling
// its default method if one is available.
func (_ZDPc *ZDPcTransactorRaw) Transfer(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _ZDPc.Contract.contract.Transfer(opts)
}

// Transact invokes the (paid) contract method with params as input values.
func (_ZDPc *ZDPcTransactorRaw) Transact(opts *bind.TransactOpts, method string, params ...interface{}) (*types.Transaction, error) {
	return _ZDPc.Contract.contract.Transact(opts, method, params...)
}

// MAXACTIVEORDER is a free data retrieval call binding the contract method 0x98692535.
//
// Solidity: function MAX_ACTIVE_ORDER() view returns(uint256)
func (_ZDPc *ZDPcCaller) MAXACTIVEORDER(opts *bind.CallOpts) (*big.Int, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "MAX_ACTIVE_ORDER")

	if err != nil {
		return *new(*big.Int), err
	}

	out0 := *abi.ConvertType(out[0], new(*big.Int)).(**big.Int)

	return out0, err

}

// MAXACTIVEORDER is a free data retrieval call binding the contract method 0x98692535.
//
// Solidity: function MAX_ACTIVE_ORDER() view returns(uint256)
func (_ZDPc *ZDPcSession) MAXACTIVEORDER() (*big.Int, error) {
	return _ZDPc.Contract.MAXACTIVEORDER(&_ZDPc.CallOpts)
}

// MAXACTIVEORDER is a free data retrieval call binding the contract method 0x98692535.
//
// Solidity: function MAX_ACTIVE_ORDER() view returns(uint256)
func (_ZDPc *ZDPcCallerSession) MAXACTIVEORDER() (*big.Int, error) {
	return _ZDPc.Contract.MAXACTIVEORDER(&_ZDPc.CallOpts)
}

// ActiveOrders is a free data retrieval call binding the contract method 0x2d375de8.
//
// Solidity: function activeOrders(address , uint256 ) view returns(uint256)
func (_ZDPc *ZDPcCaller) ActiveOrders(opts *bind.CallOpts, arg0 common.Address, arg1 *big.Int) (*big.Int, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "activeOrders", arg0, arg1)

	if err != nil {
		return *new(*big.Int), err
	}

	out0 := *abi.ConvertType(out[0], new(*big.Int)).(**big.Int)

	return out0, err

}

// ActiveOrders is a free data retrieval call binding the contract method 0x2d375de8.
//
// Solidity: function activeOrders(address , uint256 ) view returns(uint256)
func (_ZDPc *ZDPcSession) ActiveOrders(arg0 common.Address, arg1 *big.Int) (*big.Int, error) {
	return _ZDPc.Contract.ActiveOrders(&_ZDPc.CallOpts, arg0, arg1)
}

// ActiveOrders is a free data retrieval call binding the contract method 0x2d375de8.
//
// Solidity: function activeOrders(address , uint256 ) view returns(uint256)
func (_ZDPc *ZDPcCallerSession) ActiveOrders(arg0 common.Address, arg1 *big.Int) (*big.Int, error) {
	return _ZDPc.Contract.ActiveOrders(&_ZDPc.CallOpts, arg0, arg1)
}

// Agent is a free data retrieval call binding the contract method 0xf5ff5c76.
//
// Solidity: function agent() view returns(address)
func (_ZDPc *ZDPcCaller) Agent(opts *bind.CallOpts) (common.Address, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "agent")

	if err != nil {
		return *new(common.Address), err
	}

	out0 := *abi.ConvertType(out[0], new(common.Address)).(*common.Address)

	return out0, err

}

// Agent is a free data retrieval call binding the contract method 0xf5ff5c76.
//
// Solidity: function agent() view returns(address)
func (_ZDPc *ZDPcSession) Agent() (common.Address, error) {
	return _ZDPc.Contract.Agent(&_ZDPc.CallOpts)
}

// Agent is a free data retrieval call binding the contract method 0xf5ff5c76.
//
// Solidity: function agent() view returns(address)
func (_ZDPc *ZDPcCallerSession) Agent() (common.Address, error) {
	return _ZDPc.Contract.Agent(&_ZDPc.CallOpts)
}

// Gasfee is a free data retrieval call binding the contract method 0x8abfcba3.
//
// Solidity: function gasfee(address ) view returns(uint256)
func (_ZDPc *ZDPcCaller) Gasfee(opts *bind.CallOpts, arg0 common.Address) (*big.Int, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "gasfee", arg0)

	if err != nil {
		return *new(*big.Int), err
	}

	out0 := *abi.ConvertType(out[0], new(*big.Int)).(**big.Int)

	return out0, err

}

// Gasfee is a free data retrieval call binding the contract method 0x8abfcba3.
//
// Solidity: function gasfee(address ) view returns(uint256)
func (_ZDPc *ZDPcSession) Gasfee(arg0 common.Address) (*big.Int, error) {
	return _ZDPc.Contract.Gasfee(&_ZDPc.CallOpts, arg0)
}

// Gasfee is a free data retrieval call binding the contract method 0x8abfcba3.
//
// Solidity: function gasfee(address ) view returns(uint256)
func (_ZDPc *ZDPcCallerSession) Gasfee(arg0 common.Address) (*big.Int, error) {
	return _ZDPc.Contract.Gasfee(&_ZDPc.CallOpts, arg0)
}

// GetActiveOrders is a free data retrieval call binding the contract method 0xc53a490a.
//
// Solidity: function getActiveOrders(address swapper) view returns(uint256[])
func (_ZDPc *ZDPcCaller) GetActiveOrders(opts *bind.CallOpts, swapper common.Address) ([]*big.Int, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "getActiveOrders", swapper)

	if err != nil {
		return *new([]*big.Int), err
	}

	out0 := *abi.ConvertType(out[0], new([]*big.Int)).(*[]*big.Int)

	return out0, err

}

// GetActiveOrders is a free data retrieval call binding the contract method 0xc53a490a.
//
// Solidity: function getActiveOrders(address swapper) view returns(uint256[])
func (_ZDPc *ZDPcSession) GetActiveOrders(swapper common.Address) ([]*big.Int, error) {
	return _ZDPc.Contract.GetActiveOrders(&_ZDPc.CallOpts, swapper)
}

// GetActiveOrders is a free data retrieval call binding the contract method 0xc53a490a.
//
// Solidity: function getActiveOrders(address swapper) view returns(uint256[])
func (_ZDPc *ZDPcCallerSession) GetActiveOrders(swapper common.Address) ([]*big.Int, error) {
	return _ZDPc.Contract.GetActiveOrders(&_ZDPc.CallOpts, swapper)
}

// GetOrder is a free data retrieval call binding the contract method 0xedb25841.
//
// Solidity: function getOrder(address swapper, uint256 index) view returns(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16))
func (_ZDPc *ZDPcCaller) GetOrder(opts *bind.CallOpts, swapper common.Address, index *big.Int) (ZDPcOrder, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "getOrder", swapper, index)

	if err != nil {
		return *new(ZDPcOrder), err
	}

	out0 := *abi.ConvertType(out[0], new(ZDPcOrder)).(*ZDPcOrder)

	return out0, err

}

// GetOrder is a free data retrieval call binding the contract method 0xedb25841.
//
// Solidity: function getOrder(address swapper, uint256 index) view returns(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16))
func (_ZDPc *ZDPcSession) GetOrder(swapper common.Address, index *big.Int) (ZDPcOrder, error) {
	return _ZDPc.Contract.GetOrder(&_ZDPc.CallOpts, swapper, index)
}

// GetOrder is a free data retrieval call binding the contract method 0xedb25841.
//
// Solidity: function getOrder(address swapper, uint256 index) view returns(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16))
func (_ZDPc *ZDPcCallerSession) GetOrder(swapper common.Address, index *big.Int) (ZDPcOrder, error) {
	return _ZDPc.Contract.GetOrder(&_ZDPc.CallOpts, swapper, index)
}

// GetOrders is a free data retrieval call binding the contract method 0x093376fe.
//
// Solidity: function getOrders(address swapper) view returns(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16)[])
func (_ZDPc *ZDPcCaller) GetOrders(opts *bind.CallOpts, swapper common.Address) ([]ZDPcOrder, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "getOrders", swapper)

	if err != nil {
		return *new([]ZDPcOrder), err
	}

	out0 := *abi.ConvertType(out[0], new([]ZDPcOrder)).(*[]ZDPcOrder)

	return out0, err

}

// GetOrders is a free data retrieval call binding the contract method 0x093376fe.
//
// Solidity: function getOrders(address swapper) view returns(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16)[])
func (_ZDPc *ZDPcSession) GetOrders(swapper common.Address) ([]ZDPcOrder, error) {
	return _ZDPc.Contract.GetOrders(&_ZDPc.CallOpts, swapper)
}

// GetOrders is a free data retrieval call binding the contract method 0x093376fe.
//
// Solidity: function getOrders(address swapper) view returns(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16)[])
func (_ZDPc *ZDPcCallerSession) GetOrders(swapper common.Address) ([]ZDPcOrder, error) {
	return _ZDPc.Contract.GetOrders(&_ZDPc.CallOpts, swapper)
}

// Orderbook is a free data retrieval call binding the contract method 0xc7d0862d.
//
// Solidity: function orderbook(address , uint256 ) view returns((address,address,address,address,uint256,uint256,bool,bool,bytes) t, bytes16 HOsF, bytes16 HOsE)
func (_ZDPc *ZDPcCaller) Orderbook(opts *bind.CallOpts, arg0 common.Address, arg1 *big.Int) (struct {
	T    ZDPcOrderDetails
	HOsF [16]byte
	HOsE [16]byte
}, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "orderbook", arg0, arg1)

	outstruct := new(struct {
		T    ZDPcOrderDetails
		HOsF [16]byte
		HOsE [16]byte
	})
	if err != nil {
		return *outstruct, err
	}

	outstruct.T = *abi.ConvertType(out[0], new(ZDPcOrderDetails)).(*ZDPcOrderDetails)
	outstruct.HOsF = *abi.ConvertType(out[1], new([16]byte)).(*[16]byte)
	outstruct.HOsE = *abi.ConvertType(out[2], new([16]byte)).(*[16]byte)

	return *outstruct, err

}

// Orderbook is a free data retrieval call binding the contract method 0xc7d0862d.
//
// Solidity: function orderbook(address , uint256 ) view returns((address,address,address,address,uint256,uint256,bool,bool,bytes) t, bytes16 HOsF, bytes16 HOsE)
func (_ZDPc *ZDPcSession) Orderbook(arg0 common.Address, arg1 *big.Int) (struct {
	T    ZDPcOrderDetails
	HOsF [16]byte
	HOsE [16]byte
}, error) {
	return _ZDPc.Contract.Orderbook(&_ZDPc.CallOpts, arg0, arg1)
}

// Orderbook is a free data retrieval call binding the contract method 0xc7d0862d.
//
// Solidity: function orderbook(address , uint256 ) view returns((address,address,address,address,uint256,uint256,bool,bool,bytes) t, bytes16 HOsF, bytes16 HOsE)
func (_ZDPc *ZDPcCallerSession) Orderbook(arg0 common.Address, arg1 *big.Int) (struct {
	T    ZDPcOrderDetails
	HOsF [16]byte
	HOsE [16]byte
}, error) {
	return _ZDPc.Contract.Orderbook(&_ZDPc.CallOpts, arg0, arg1)
}

// Owner is a free data retrieval call binding the contract method 0x8da5cb5b.
//
// Solidity: function owner() view returns(address)
func (_ZDPc *ZDPcCaller) Owner(opts *bind.CallOpts) (common.Address, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "owner")

	if err != nil {
		return *new(common.Address), err
	}

	out0 := *abi.ConvertType(out[0], new(common.Address)).(*common.Address)

	return out0, err

}

// Owner is a free data retrieval call binding the contract method 0x8da5cb5b.
//
// Solidity: function owner() view returns(address)
func (_ZDPc *ZDPcSession) Owner() (common.Address, error) {
	return _ZDPc.Contract.Owner(&_ZDPc.CallOpts)
}

// Owner is a free data retrieval call binding the contract method 0x8da5cb5b.
//
// Solidity: function owner() view returns(address)
func (_ZDPc *ZDPcCallerSession) Owner() (common.Address, error) {
	return _ZDPc.Contract.Owner(&_ZDPc.CallOpts)
}

// PendingOwner is a free data retrieval call binding the contract method 0xe30c3978.
//
// Solidity: function pendingOwner() view returns(address)
func (_ZDPc *ZDPcCaller) PendingOwner(opts *bind.CallOpts) (common.Address, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "pendingOwner")

	if err != nil {
		return *new(common.Address), err
	}

	out0 := *abi.ConvertType(out[0], new(common.Address)).(*common.Address)

	return out0, err

}

// PendingOwner is a free data retrieval call binding the contract method 0xe30c3978.
//
// Solidity: function pendingOwner() view returns(address)
func (_ZDPc *ZDPcSession) PendingOwner() (common.Address, error) {
	return _ZDPc.Contract.PendingOwner(&_ZDPc.CallOpts)
}

// PendingOwner is a free data retrieval call binding the contract method 0xe30c3978.
//
// Solidity: function pendingOwner() view returns(address)
func (_ZDPc *ZDPcCallerSession) PendingOwner() (common.Address, error) {
	return _ZDPc.Contract.PendingOwner(&_ZDPc.CallOpts)
}

// Router is a free data retrieval call binding the contract method 0xf887ea40.
//
// Solidity: function router() view returns(address)
func (_ZDPc *ZDPcCaller) Router(opts *bind.CallOpts) (common.Address, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "router")

	if err != nil {
		return *new(common.Address), err
	}

	out0 := *abi.ConvertType(out[0], new(common.Address)).(*common.Address)

	return out0, err

}

// Router is a free data retrieval call binding the contract method 0xf887ea40.
//
// Solidity: function router() view returns(address)
func (_ZDPc *ZDPcSession) Router() (common.Address, error) {
	return _ZDPc.Contract.Router(&_ZDPc.CallOpts)
}

// Router is a free data retrieval call binding the contract method 0xf887ea40.
//
// Solidity: function router() view returns(address)
func (_ZDPc *ZDPcCallerSession) Router() (common.Address, error) {
	return _ZDPc.Contract.Router(&_ZDPc.CallOpts)
}

// Verifier is a free data retrieval call binding the contract method 0x2b7ac3f3.
//
// Solidity: function verifier() view returns(address)
func (_ZDPc *ZDPcCaller) Verifier(opts *bind.CallOpts) (common.Address, error) {
	var out []interface{}
	err := _ZDPc.contract.Call(opts, &out, "verifier")

	if err != nil {
		return *new(common.Address), err
	}

	out0 := *abi.ConvertType(out[0], new(common.Address)).(*common.Address)

	return out0, err

}

// Verifier is a free data retrieval call binding the contract method 0x2b7ac3f3.
//
// Solidity: function verifier() view returns(address)
func (_ZDPc *ZDPcSession) Verifier() (common.Address, error) {
	return _ZDPc.Contract.Verifier(&_ZDPc.CallOpts)
}

// Verifier is a free data retrieval call binding the contract method 0x2b7ac3f3.
//
// Solidity: function verifier() view returns(address)
func (_ZDPc *ZDPcCallerSession) Verifier() (common.Address, error) {
	return _ZDPc.Contract.Verifier(&_ZDPc.CallOpts)
}

// AcceptOwnership is a paid mutator transaction binding the contract method 0x79ba5097.
//
// Solidity: function acceptOwnership() returns()
func (_ZDPc *ZDPcTransactor) AcceptOwnership(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "acceptOwnership")
}

// AcceptOwnership is a paid mutator transaction binding the contract method 0x79ba5097.
//
// Solidity: function acceptOwnership() returns()
func (_ZDPc *ZDPcSession) AcceptOwnership() (*types.Transaction, error) {
	return _ZDPc.Contract.AcceptOwnership(&_ZDPc.TransactOpts)
}

// AcceptOwnership is a paid mutator transaction binding the contract method 0x79ba5097.
//
// Solidity: function acceptOwnership() returns()
func (_ZDPc *ZDPcTransactorSession) AcceptOwnership() (*types.Transaction, error) {
	return _ZDPc.Contract.AcceptOwnership(&_ZDPc.TransactOpts)
}

// AddPendingOrder is a paid mutator transaction binding the contract method 0xc680993b.
//
// Solidity: function addPendingOrder(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16) _order) returns()
func (_ZDPc *ZDPcTransactor) AddPendingOrder(opts *bind.TransactOpts, _order ZDPcOrder) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "addPendingOrder", _order)
}

// AddPendingOrder is a paid mutator transaction binding the contract method 0xc680993b.
//
// Solidity: function addPendingOrder(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16) _order) returns()
func (_ZDPc *ZDPcSession) AddPendingOrder(_order ZDPcOrder) (*types.Transaction, error) {
	return _ZDPc.Contract.AddPendingOrder(&_ZDPc.TransactOpts, _order)
}

// AddPendingOrder is a paid mutator transaction binding the contract method 0xc680993b.
//
// Solidity: function addPendingOrder(((address,address,address,address,uint256,uint256,bool,bool,bytes),bytes16,bytes16) _order) returns()
func (_ZDPc *ZDPcTransactorSession) AddPendingOrder(_order ZDPcOrder) (*types.Transaction, error) {
	return _ZDPc.Contract.AddPendingOrder(&_ZDPc.TransactOpts, _order)
}

// CancelOrder is a paid mutator transaction binding the contract method 0x514fcac7.
//
// Solidity: function cancelOrder(uint256 index) returns()
func (_ZDPc *ZDPcTransactor) CancelOrder(opts *bind.TransactOpts, index *big.Int) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "cancelOrder", index)
}

// CancelOrder is a paid mutator transaction binding the contract method 0x514fcac7.
//
// Solidity: function cancelOrder(uint256 index) returns()
func (_ZDPc *ZDPcSession) CancelOrder(index *big.Int) (*types.Transaction, error) {
	return _ZDPc.Contract.CancelOrder(&_ZDPc.TransactOpts, index)
}

// CancelOrder is a paid mutator transaction binding the contract method 0x514fcac7.
//
// Solidity: function cancelOrder(uint256 index) returns()
func (_ZDPc *ZDPcTransactorSession) CancelOrder(index *big.Int) (*types.Transaction, error) {
	return _ZDPc.Contract.CancelOrder(&_ZDPc.TransactOpts, index)
}

// DepositForGasFee is a paid mutator transaction binding the contract method 0x6b5da867.
//
// Solidity: function depositForGasFee(address swapper) payable returns()
func (_ZDPc *ZDPcTransactor) DepositForGasFee(opts *bind.TransactOpts, swapper common.Address) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "depositForGasFee", swapper)
}

// DepositForGasFee is a paid mutator transaction binding the contract method 0x6b5da867.
//
// Solidity: function depositForGasFee(address swapper) payable returns()
func (_ZDPc *ZDPcSession) DepositForGasFee(swapper common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.DepositForGasFee(&_ZDPc.TransactOpts, swapper)
}

// DepositForGasFee is a paid mutator transaction binding the contract method 0x6b5da867.
//
// Solidity: function depositForGasFee(address swapper) payable returns()
func (_ZDPc *ZDPcTransactorSession) DepositForGasFee(swapper common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.DepositForGasFee(&_ZDPc.TransactOpts, swapper)
}

// RenounceOwnership is a paid mutator transaction binding the contract method 0x715018a6.
//
// Solidity: function renounceOwnership() returns()
func (_ZDPc *ZDPcTransactor) RenounceOwnership(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "renounceOwnership")
}

// RenounceOwnership is a paid mutator transaction binding the contract method 0x715018a6.
//
// Solidity: function renounceOwnership() returns()
func (_ZDPc *ZDPcSession) RenounceOwnership() (*types.Transaction, error) {
	return _ZDPc.Contract.RenounceOwnership(&_ZDPc.TransactOpts)
}

// RenounceOwnership is a paid mutator transaction binding the contract method 0x715018a6.
//
// Solidity: function renounceOwnership() returns()
func (_ZDPc *ZDPcTransactorSession) RenounceOwnership() (*types.Transaction, error) {
	return _ZDPc.Contract.RenounceOwnership(&_ZDPc.TransactOpts)
}

// SetAgent is a paid mutator transaction binding the contract method 0xbcf685ed.
//
// Solidity: function setAgent(address _agent) returns()
func (_ZDPc *ZDPcTransactor) SetAgent(opts *bind.TransactOpts, _agent common.Address) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "setAgent", _agent)
}

// SetAgent is a paid mutator transaction binding the contract method 0xbcf685ed.
//
// Solidity: function setAgent(address _agent) returns()
func (_ZDPc *ZDPcSession) SetAgent(_agent common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.SetAgent(&_ZDPc.TransactOpts, _agent)
}

// SetAgent is a paid mutator transaction binding the contract method 0xbcf685ed.
//
// Solidity: function setAgent(address _agent) returns()
func (_ZDPc *ZDPcTransactorSession) SetAgent(_agent common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.SetAgent(&_ZDPc.TransactOpts, _agent)
}

// SetRouter is a paid mutator transaction binding the contract method 0xc0d78655.
//
// Solidity: function setRouter(address _router) returns()
func (_ZDPc *ZDPcTransactor) SetRouter(opts *bind.TransactOpts, _router common.Address) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "setRouter", _router)
}

// SetRouter is a paid mutator transaction binding the contract method 0xc0d78655.
//
// Solidity: function setRouter(address _router) returns()
func (_ZDPc *ZDPcSession) SetRouter(_router common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.SetRouter(&_ZDPc.TransactOpts, _router)
}

// SetRouter is a paid mutator transaction binding the contract method 0xc0d78655.
//
// Solidity: function setRouter(address _router) returns()
func (_ZDPc *ZDPcTransactorSession) SetRouter(_router common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.SetRouter(&_ZDPc.TransactOpts, _router)
}

// SetVerifier is a paid mutator transaction binding the contract method 0x5437988d.
//
// Solidity: function setVerifier(address _verifier) returns()
func (_ZDPc *ZDPcTransactor) SetVerifier(opts *bind.TransactOpts, _verifier common.Address) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "setVerifier", _verifier)
}

// SetVerifier is a paid mutator transaction binding the contract method 0x5437988d.
//
// Solidity: function setVerifier(address _verifier) returns()
func (_ZDPc *ZDPcSession) SetVerifier(_verifier common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.SetVerifier(&_ZDPc.TransactOpts, _verifier)
}

// SetVerifier is a paid mutator transaction binding the contract method 0x5437988d.
//
// Solidity: function setVerifier(address _verifier) returns()
func (_ZDPc *ZDPcTransactorSession) SetVerifier(_verifier common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.SetVerifier(&_ZDPc.TransactOpts, _verifier)
}

// SwapForward is a paid mutator transaction binding the contract method 0x458f9a86.
//
// Solidity: function swapForward(uint256[2] _proofA, uint256[2][2] _proofB, uint256[2] _proofC, address swapper, uint256 index, uint256 a0e, uint256 a1m, uint256 _gasFee, uint8 _type) returns()
func (_ZDPc *ZDPcTransactor) SwapForward(opts *bind.TransactOpts, _proofA [2]*big.Int, _proofB [2][2]*big.Int, _proofC [2]*big.Int, swapper common.Address, index *big.Int, a0e *big.Int, a1m *big.Int, _gasFee *big.Int, _type uint8) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "swapForward", _proofA, _proofB, _proofC, swapper, index, a0e, a1m, _gasFee, _type)
}

// SwapForward is a paid mutator transaction binding the contract method 0x458f9a86.
//
// Solidity: function swapForward(uint256[2] _proofA, uint256[2][2] _proofB, uint256[2] _proofC, address swapper, uint256 index, uint256 a0e, uint256 a1m, uint256 _gasFee, uint8 _type) returns()
func (_ZDPc *ZDPcSession) SwapForward(_proofA [2]*big.Int, _proofB [2][2]*big.Int, _proofC [2]*big.Int, swapper common.Address, index *big.Int, a0e *big.Int, a1m *big.Int, _gasFee *big.Int, _type uint8) (*types.Transaction, error) {
	return _ZDPc.Contract.SwapForward(&_ZDPc.TransactOpts, _proofA, _proofB, _proofC, swapper, index, a0e, a1m, _gasFee, _type)
}

// SwapForward is a paid mutator transaction binding the contract method 0x458f9a86.
//
// Solidity: function swapForward(uint256[2] _proofA, uint256[2][2] _proofB, uint256[2] _proofC, address swapper, uint256 index, uint256 a0e, uint256 a1m, uint256 _gasFee, uint8 _type) returns()
func (_ZDPc *ZDPcTransactorSession) SwapForward(_proofA [2]*big.Int, _proofB [2][2]*big.Int, _proofC [2]*big.Int, swapper common.Address, index *big.Int, a0e *big.Int, a1m *big.Int, _gasFee *big.Int, _type uint8) (*types.Transaction, error) {
	return _ZDPc.Contract.SwapForward(&_ZDPc.TransactOpts, _proofA, _proofB, _proofC, swapper, index, a0e, a1m, _gasFee, _type)
}

// TransferOwnership is a paid mutator transaction binding the contract method 0xf2fde38b.
//
// Solidity: function transferOwnership(address newOwner) returns()
func (_ZDPc *ZDPcTransactor) TransferOwnership(opts *bind.TransactOpts, newOwner common.Address) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "transferOwnership", newOwner)
}

// TransferOwnership is a paid mutator transaction binding the contract method 0xf2fde38b.
//
// Solidity: function transferOwnership(address newOwner) returns()
func (_ZDPc *ZDPcSession) TransferOwnership(newOwner common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.TransferOwnership(&_ZDPc.TransactOpts, newOwner)
}

// TransferOwnership is a paid mutator transaction binding the contract method 0xf2fde38b.
//
// Solidity: function transferOwnership(address newOwner) returns()
func (_ZDPc *ZDPcTransactorSession) TransferOwnership(newOwner common.Address) (*types.Transaction, error) {
	return _ZDPc.Contract.TransferOwnership(&_ZDPc.TransactOpts, newOwner)
}

// WithdrawGasFee is a paid mutator transaction binding the contract method 0x19c0f1ce.
//
// Solidity: function withdrawGasFee(uint256 amount) returns()
func (_ZDPc *ZDPcTransactor) WithdrawGasFee(opts *bind.TransactOpts, amount *big.Int) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "withdrawGasFee", amount)
}

// WithdrawGasFee is a paid mutator transaction binding the contract method 0x19c0f1ce.
//
// Solidity: function withdrawGasFee(uint256 amount) returns()
func (_ZDPc *ZDPcSession) WithdrawGasFee(amount *big.Int) (*types.Transaction, error) {
	return _ZDPc.Contract.WithdrawGasFee(&_ZDPc.TransactOpts, amount)
}

// WithdrawGasFee is a paid mutator transaction binding the contract method 0x19c0f1ce.
//
// Solidity: function withdrawGasFee(uint256 amount) returns()
func (_ZDPc *ZDPcTransactorSession) WithdrawGasFee(amount *big.Int) (*types.Transaction, error) {
	return _ZDPc.Contract.WithdrawGasFee(&_ZDPc.TransactOpts, amount)
}

// WithdrawTakenFee is a paid mutator transaction binding the contract method 0x56ab9955.
//
// Solidity: function withdrawTakenFee() returns()
func (_ZDPc *ZDPcTransactor) WithdrawTakenFee(opts *bind.TransactOpts) (*types.Transaction, error) {
	return _ZDPc.contract.Transact(opts, "withdrawTakenFee")
}

// WithdrawTakenFee is a paid mutator transaction binding the contract method 0x56ab9955.
//
// Solidity: function withdrawTakenFee() returns()
func (_ZDPc *ZDPcSession) WithdrawTakenFee() (*types.Transaction, error) {
	return _ZDPc.Contract.WithdrawTakenFee(&_ZDPc.TransactOpts)
}

// WithdrawTakenFee is a paid mutator transaction binding the contract method 0x56ab9955.
//
// Solidity: function withdrawTakenFee() returns()
func (_ZDPc *ZDPcTransactorSession) WithdrawTakenFee() (*types.Transaction, error) {
	return _ZDPc.Contract.WithdrawTakenFee(&_ZDPc.TransactOpts)
}

// ZDPcAgentChangedIterator is returned from FilterAgentChanged and is used to iterate over the raw logs and unpacked data for AgentChanged events raised by the ZDPc contract.
type ZDPcAgentChangedIterator struct {
	Event *ZDPcAgentChanged // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcAgentChangedIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcAgentChanged)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcAgentChanged)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcAgentChangedIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcAgentChangedIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcAgentChanged represents a AgentChanged event raised by the ZDPc contract.
type ZDPcAgentChanged struct {
	OldAgent common.Address
	NewAgent common.Address
	Raw      types.Log // Blockchain specific contextual infos
}

// FilterAgentChanged is a free log retrieval operation binding the contract event 0xb21f1bf0d206b43eb02be4f423c2788a95affbda226125eaecabe3def8ba5c42.
//
// Solidity: event AgentChanged(address indexed oldAgent, address indexed newAgent)
func (_ZDPc *ZDPcFilterer) FilterAgentChanged(opts *bind.FilterOpts, oldAgent []common.Address, newAgent []common.Address) (*ZDPcAgentChangedIterator, error) {

	var oldAgentRule []interface{}
	for _, oldAgentItem := range oldAgent {
		oldAgentRule = append(oldAgentRule, oldAgentItem)
	}
	var newAgentRule []interface{}
	for _, newAgentItem := range newAgent {
		newAgentRule = append(newAgentRule, newAgentItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "AgentChanged", oldAgentRule, newAgentRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcAgentChangedIterator{contract: _ZDPc.contract, event: "AgentChanged", logs: logs, sub: sub}, nil
}

// WatchAgentChanged is a free log subscription operation binding the contract event 0xb21f1bf0d206b43eb02be4f423c2788a95affbda226125eaecabe3def8ba5c42.
//
// Solidity: event AgentChanged(address indexed oldAgent, address indexed newAgent)
func (_ZDPc *ZDPcFilterer) WatchAgentChanged(opts *bind.WatchOpts, sink chan<- *ZDPcAgentChanged, oldAgent []common.Address, newAgent []common.Address) (event.Subscription, error) {

	var oldAgentRule []interface{}
	for _, oldAgentItem := range oldAgent {
		oldAgentRule = append(oldAgentRule, oldAgentItem)
	}
	var newAgentRule []interface{}
	for _, newAgentItem := range newAgent {
		newAgentRule = append(newAgentRule, newAgentItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "AgentChanged", oldAgentRule, newAgentRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcAgentChanged)
				if err := _ZDPc.contract.UnpackLog(event, "AgentChanged", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseAgentChanged is a log parse operation binding the contract event 0xb21f1bf0d206b43eb02be4f423c2788a95affbda226125eaecabe3def8ba5c42.
//
// Solidity: event AgentChanged(address indexed oldAgent, address indexed newAgent)
func (_ZDPc *ZDPcFilterer) ParseAgentChanged(log types.Log) (*ZDPcAgentChanged, error) {
	event := new(ZDPcAgentChanged)
	if err := _ZDPc.contract.UnpackLog(event, "AgentChanged", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcFeeDepositIterator is returned from FilterFeeDeposit and is used to iterate over the raw logs and unpacked data for FeeDeposit events raised by the ZDPc contract.
type ZDPcFeeDepositIterator struct {
	Event *ZDPcFeeDeposit // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcFeeDepositIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcFeeDeposit)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcFeeDeposit)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcFeeDepositIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcFeeDepositIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcFeeDeposit represents a FeeDeposit event raised by the ZDPc contract.
type ZDPcFeeDeposit struct {
	Swapper common.Address
	Fee     *big.Int
	Raw     types.Log // Blockchain specific contextual infos
}

// FilterFeeDeposit is a free log retrieval operation binding the contract event 0xa8491ef03ac2868e696ed75957d04a1175eb88946dbc13ee05e75040c8db91d9.
//
// Solidity: event FeeDeposit(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) FilterFeeDeposit(opts *bind.FilterOpts, swapper []common.Address, fee []*big.Int) (*ZDPcFeeDepositIterator, error) {

	var swapperRule []interface{}
	for _, swapperItem := range swapper {
		swapperRule = append(swapperRule, swapperItem)
	}
	var feeRule []interface{}
	for _, feeItem := range fee {
		feeRule = append(feeRule, feeItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "FeeDeposit", swapperRule, feeRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcFeeDepositIterator{contract: _ZDPc.contract, event: "FeeDeposit", logs: logs, sub: sub}, nil
}

// WatchFeeDeposit is a free log subscription operation binding the contract event 0xa8491ef03ac2868e696ed75957d04a1175eb88946dbc13ee05e75040c8db91d9.
//
// Solidity: event FeeDeposit(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) WatchFeeDeposit(opts *bind.WatchOpts, sink chan<- *ZDPcFeeDeposit, swapper []common.Address, fee []*big.Int) (event.Subscription, error) {

	var swapperRule []interface{}
	for _, swapperItem := range swapper {
		swapperRule = append(swapperRule, swapperItem)
	}
	var feeRule []interface{}
	for _, feeItem := range fee {
		feeRule = append(feeRule, feeItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "FeeDeposit", swapperRule, feeRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcFeeDeposit)
				if err := _ZDPc.contract.UnpackLog(event, "FeeDeposit", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseFeeDeposit is a log parse operation binding the contract event 0xa8491ef03ac2868e696ed75957d04a1175eb88946dbc13ee05e75040c8db91d9.
//
// Solidity: event FeeDeposit(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) ParseFeeDeposit(log types.Log) (*ZDPcFeeDeposit, error) {
	event := new(ZDPcFeeDeposit)
	if err := _ZDPc.contract.UnpackLog(event, "FeeDeposit", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcFeeTakenIterator is returned from FilterFeeTaken and is used to iterate over the raw logs and unpacked data for FeeTaken events raised by the ZDPc contract.
type ZDPcFeeTakenIterator struct {
	Event *ZDPcFeeTaken // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcFeeTakenIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcFeeTaken)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcFeeTaken)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcFeeTakenIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcFeeTakenIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcFeeTaken represents a FeeTaken event raised by the ZDPc contract.
type ZDPcFeeTaken struct {
	Swapper common.Address
	Fee     *big.Int
	Raw     types.Log // Blockchain specific contextual infos
}

// FilterFeeTaken is a free log retrieval operation binding the contract event 0x1b02d16d3c4c6fce038de5403c8352eb1eb62bc6915b6848683de52a24a723f8.
//
// Solidity: event FeeTaken(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) FilterFeeTaken(opts *bind.FilterOpts, swapper []common.Address, fee []*big.Int) (*ZDPcFeeTakenIterator, error) {

	var swapperRule []interface{}
	for _, swapperItem := range swapper {
		swapperRule = append(swapperRule, swapperItem)
	}
	var feeRule []interface{}
	for _, feeItem := range fee {
		feeRule = append(feeRule, feeItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "FeeTaken", swapperRule, feeRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcFeeTakenIterator{contract: _ZDPc.contract, event: "FeeTaken", logs: logs, sub: sub}, nil
}

// WatchFeeTaken is a free log subscription operation binding the contract event 0x1b02d16d3c4c6fce038de5403c8352eb1eb62bc6915b6848683de52a24a723f8.
//
// Solidity: event FeeTaken(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) WatchFeeTaken(opts *bind.WatchOpts, sink chan<- *ZDPcFeeTaken, swapper []common.Address, fee []*big.Int) (event.Subscription, error) {

	var swapperRule []interface{}
	for _, swapperItem := range swapper {
		swapperRule = append(swapperRule, swapperItem)
	}
	var feeRule []interface{}
	for _, feeItem := range fee {
		feeRule = append(feeRule, feeItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "FeeTaken", swapperRule, feeRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcFeeTaken)
				if err := _ZDPc.contract.UnpackLog(event, "FeeTaken", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseFeeTaken is a log parse operation binding the contract event 0x1b02d16d3c4c6fce038de5403c8352eb1eb62bc6915b6848683de52a24a723f8.
//
// Solidity: event FeeTaken(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) ParseFeeTaken(log types.Log) (*ZDPcFeeTaken, error) {
	event := new(ZDPcFeeTaken)
	if err := _ZDPc.contract.UnpackLog(event, "FeeTaken", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcFeeWithdrawnIterator is returned from FilterFeeWithdrawn and is used to iterate over the raw logs and unpacked data for FeeWithdrawn events raised by the ZDPc contract.
type ZDPcFeeWithdrawnIterator struct {
	Event *ZDPcFeeWithdrawn // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcFeeWithdrawnIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcFeeWithdrawn)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcFeeWithdrawn)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcFeeWithdrawnIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcFeeWithdrawnIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcFeeWithdrawn represents a FeeWithdrawn event raised by the ZDPc contract.
type ZDPcFeeWithdrawn struct {
	Swapper common.Address
	Fee     *big.Int
	Raw     types.Log // Blockchain specific contextual infos
}

// FilterFeeWithdrawn is a free log retrieval operation binding the contract event 0x78473f3f373f7673597f4f0fa5873cb4d375fea6d4339ad6b56dbd411513cb3f.
//
// Solidity: event FeeWithdrawn(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) FilterFeeWithdrawn(opts *bind.FilterOpts, swapper []common.Address, fee []*big.Int) (*ZDPcFeeWithdrawnIterator, error) {

	var swapperRule []interface{}
	for _, swapperItem := range swapper {
		swapperRule = append(swapperRule, swapperItem)
	}
	var feeRule []interface{}
	for _, feeItem := range fee {
		feeRule = append(feeRule, feeItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "FeeWithdrawn", swapperRule, feeRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcFeeWithdrawnIterator{contract: _ZDPc.contract, event: "FeeWithdrawn", logs: logs, sub: sub}, nil
}

// WatchFeeWithdrawn is a free log subscription operation binding the contract event 0x78473f3f373f7673597f4f0fa5873cb4d375fea6d4339ad6b56dbd411513cb3f.
//
// Solidity: event FeeWithdrawn(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) WatchFeeWithdrawn(opts *bind.WatchOpts, sink chan<- *ZDPcFeeWithdrawn, swapper []common.Address, fee []*big.Int) (event.Subscription, error) {

	var swapperRule []interface{}
	for _, swapperItem := range swapper {
		swapperRule = append(swapperRule, swapperItem)
	}
	var feeRule []interface{}
	for _, feeItem := range fee {
		feeRule = append(feeRule, feeItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "FeeWithdrawn", swapperRule, feeRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcFeeWithdrawn)
				if err := _ZDPc.contract.UnpackLog(event, "FeeWithdrawn", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseFeeWithdrawn is a log parse operation binding the contract event 0x78473f3f373f7673597f4f0fa5873cb4d375fea6d4339ad6b56dbd411513cb3f.
//
// Solidity: event FeeWithdrawn(address indexed swapper, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) ParseFeeWithdrawn(log types.Log) (*ZDPcFeeWithdrawn, error) {
	event := new(ZDPcFeeWithdrawn)
	if err := _ZDPc.contract.UnpackLog(event, "FeeWithdrawn", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcHOSIterator is returned from FilterHOS and is used to iterate over the raw logs and unpacked data for HOS events raised by the ZDPc contract.
type ZDPcHOSIterator struct {
	Event *ZDPcHOS // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcHOSIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcHOS)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcHOS)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcHOSIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcHOSIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcHOS represents a HOS event raised by the ZDPc contract.
type ZDPcHOS struct {
	HOsF [16]byte
	HOsE [16]byte
	Raw  types.Log // Blockchain specific contextual infos
}

// FilterHOS is a free log retrieval operation binding the contract event 0xd5a10753f9b1346718a3088dcb16b007cc314e04c2da19a1bd2578369a436719.
//
// Solidity: event HOS(bytes16 indexed HOsF, bytes16 indexed HOsE)
func (_ZDPc *ZDPcFilterer) FilterHOS(opts *bind.FilterOpts, HOsF [][16]byte, HOsE [][16]byte) (*ZDPcHOSIterator, error) {

	var HOsFRule []interface{}
	for _, HOsFItem := range HOsF {
		HOsFRule = append(HOsFRule, HOsFItem)
	}
	var HOsERule []interface{}
	for _, HOsEItem := range HOsE {
		HOsERule = append(HOsERule, HOsEItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "HOS", HOsFRule, HOsERule)
	if err != nil {
		return nil, err
	}
	return &ZDPcHOSIterator{contract: _ZDPc.contract, event: "HOS", logs: logs, sub: sub}, nil
}

// WatchHOS is a free log subscription operation binding the contract event 0xd5a10753f9b1346718a3088dcb16b007cc314e04c2da19a1bd2578369a436719.
//
// Solidity: event HOS(bytes16 indexed HOsF, bytes16 indexed HOsE)
func (_ZDPc *ZDPcFilterer) WatchHOS(opts *bind.WatchOpts, sink chan<- *ZDPcHOS, HOsF [][16]byte, HOsE [][16]byte) (event.Subscription, error) {

	var HOsFRule []interface{}
	for _, HOsFItem := range HOsF {
		HOsFRule = append(HOsFRule, HOsFItem)
	}
	var HOsERule []interface{}
	for _, HOsEItem := range HOsE {
		HOsERule = append(HOsERule, HOsEItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "HOS", HOsFRule, HOsERule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcHOS)
				if err := _ZDPc.contract.UnpackLog(event, "HOS", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseHOS is a log parse operation binding the contract event 0xd5a10753f9b1346718a3088dcb16b007cc314e04c2da19a1bd2578369a436719.
//
// Solidity: event HOS(bytes16 indexed HOsF, bytes16 indexed HOsE)
func (_ZDPc *ZDPcFilterer) ParseHOS(log types.Log) (*ZDPcHOS, error) {
	event := new(ZDPcHOS)
	if err := _ZDPc.contract.UnpackLog(event, "HOS", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcOrderCancelledIterator is returned from FilterOrderCancelled and is used to iterate over the raw logs and unpacked data for OrderCancelled events raised by the ZDPc contract.
type ZDPcOrderCancelledIterator struct {
	Event *ZDPcOrderCancelled // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcOrderCancelledIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcOrderCancelled)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcOrderCancelled)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcOrderCancelledIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcOrderCancelledIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcOrderCancelled represents a OrderCancelled event raised by the ZDPc contract.
type ZDPcOrderCancelled struct {
	Swapper         common.Address
	Index           *big.Int
	TokenIn         common.Address
	TokenOut        common.Address
	ExchangeRate    *big.Int
	Deadline        *big.Int
	OrderIsExecuted bool
	IsMultiPath     bool
	EncodedPath     []byte
	Raw             types.Log // Blockchain specific contextual infos
}

// FilterOrderCancelled is a free log retrieval operation binding the contract event 0x0d0c5b825055dc54b5672a00b6c715ed19876d93d8f0cf0a241787c52a25ac30.
//
// Solidity: event OrderCancelled(address swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) FilterOrderCancelled(opts *bind.FilterOpts, index []*big.Int) (*ZDPcOrderCancelledIterator, error) {

	var indexRule []interface{}
	for _, indexItem := range index {
		indexRule = append(indexRule, indexItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "OrderCancelled", indexRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcOrderCancelledIterator{contract: _ZDPc.contract, event: "OrderCancelled", logs: logs, sub: sub}, nil
}

// WatchOrderCancelled is a free log subscription operation binding the contract event 0x0d0c5b825055dc54b5672a00b6c715ed19876d93d8f0cf0a241787c52a25ac30.
//
// Solidity: event OrderCancelled(address swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) WatchOrderCancelled(opts *bind.WatchOpts, sink chan<- *ZDPcOrderCancelled, index []*big.Int) (event.Subscription, error) {

	var indexRule []interface{}
	for _, indexItem := range index {
		indexRule = append(indexRule, indexItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "OrderCancelled", indexRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcOrderCancelled)
				if err := _ZDPc.contract.UnpackLog(event, "OrderCancelled", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseOrderCancelled is a log parse operation binding the contract event 0x0d0c5b825055dc54b5672a00b6c715ed19876d93d8f0cf0a241787c52a25ac30.
//
// Solidity: event OrderCancelled(address swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) ParseOrderCancelled(log types.Log) (*ZDPcOrderCancelled, error) {
	event := new(ZDPcOrderCancelled)
	if err := _ZDPc.contract.UnpackLog(event, "OrderCancelled", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcOrderExecutedIterator is returned from FilterOrderExecuted and is used to iterate over the raw logs and unpacked data for OrderExecuted events raised by the ZDPc contract.
type ZDPcOrderExecutedIterator struct {
	Event *ZDPcOrderExecuted // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcOrderExecutedIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcOrderExecuted)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcOrderExecuted)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcOrderExecutedIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcOrderExecutedIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcOrderExecuted represents a OrderExecuted event raised by the ZDPc contract.
type ZDPcOrderExecuted struct {
	Swapper         common.Address
	Index           *big.Int
	TokenIn         common.Address
	TokenOut        common.Address
	ExchangeRate    *big.Int
	Deadline        *big.Int
	OrderIsExecuted bool
	IsMultiPath     bool
	EncodedPath     []byte
	Raw             types.Log // Blockchain specific contextual infos
}

// FilterOrderExecuted is a free log retrieval operation binding the contract event 0x2a7f4b32e927ce7f1855229a8d7d28d0d13086e3e06df8682b32e0e8d1c7c070.
//
// Solidity: event OrderExecuted(address swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) FilterOrderExecuted(opts *bind.FilterOpts, index []*big.Int) (*ZDPcOrderExecutedIterator, error) {

	var indexRule []interface{}
	for _, indexItem := range index {
		indexRule = append(indexRule, indexItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "OrderExecuted", indexRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcOrderExecutedIterator{contract: _ZDPc.contract, event: "OrderExecuted", logs: logs, sub: sub}, nil
}

// WatchOrderExecuted is a free log subscription operation binding the contract event 0x2a7f4b32e927ce7f1855229a8d7d28d0d13086e3e06df8682b32e0e8d1c7c070.
//
// Solidity: event OrderExecuted(address swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) WatchOrderExecuted(opts *bind.WatchOpts, sink chan<- *ZDPcOrderExecuted, index []*big.Int) (event.Subscription, error) {

	var indexRule []interface{}
	for _, indexItem := range index {
		indexRule = append(indexRule, indexItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "OrderExecuted", indexRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcOrderExecuted)
				if err := _ZDPc.contract.UnpackLog(event, "OrderExecuted", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseOrderExecuted is a log parse operation binding the contract event 0x2a7f4b32e927ce7f1855229a8d7d28d0d13086e3e06df8682b32e0e8d1c7c070.
//
// Solidity: event OrderExecuted(address swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) ParseOrderExecuted(log types.Log) (*ZDPcOrderExecuted, error) {
	event := new(ZDPcOrderExecuted)
	if err := _ZDPc.contract.UnpackLog(event, "OrderExecuted", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcOrderStoredIterator is returned from FilterOrderStored and is used to iterate over the raw logs and unpacked data for OrderStored events raised by the ZDPc contract.
type ZDPcOrderStoredIterator struct {
	Event *ZDPcOrderStored // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcOrderStoredIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcOrderStored)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcOrderStored)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcOrderStoredIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcOrderStoredIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcOrderStored represents a OrderStored event raised by the ZDPc contract.
type ZDPcOrderStored struct {
	Swapper         common.Address
	Index           *big.Int
	TokenIn         common.Address
	TokenOut        common.Address
	ExchangeRate    *big.Int
	Deadline        *big.Int
	OrderIsExecuted bool
	IsMultiPath     bool
	EncodedPath     []byte
	Raw             types.Log // Blockchain specific contextual infos
}

// FilterOrderStored is a free log retrieval operation binding the contract event 0xa752f66e80f42a9cb846f9ceea27b98533a156c48dec204e9ec30f76dab78b81.
//
// Solidity: event OrderStored(address indexed swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) FilterOrderStored(opts *bind.FilterOpts, swapper []common.Address, index []*big.Int) (*ZDPcOrderStoredIterator, error) {

	var swapperRule []interface{}
	for _, swapperItem := range swapper {
		swapperRule = append(swapperRule, swapperItem)
	}
	var indexRule []interface{}
	for _, indexItem := range index {
		indexRule = append(indexRule, indexItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "OrderStored", swapperRule, indexRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcOrderStoredIterator{contract: _ZDPc.contract, event: "OrderStored", logs: logs, sub: sub}, nil
}

// WatchOrderStored is a free log subscription operation binding the contract event 0xa752f66e80f42a9cb846f9ceea27b98533a156c48dec204e9ec30f76dab78b81.
//
// Solidity: event OrderStored(address indexed swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) WatchOrderStored(opts *bind.WatchOpts, sink chan<- *ZDPcOrderStored, swapper []common.Address, index []*big.Int) (event.Subscription, error) {

	var swapperRule []interface{}
	for _, swapperItem := range swapper {
		swapperRule = append(swapperRule, swapperItem)
	}
	var indexRule []interface{}
	for _, indexItem := range index {
		indexRule = append(indexRule, indexItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "OrderStored", swapperRule, indexRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcOrderStored)
				if err := _ZDPc.contract.UnpackLog(event, "OrderStored", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseOrderStored is a log parse operation binding the contract event 0xa752f66e80f42a9cb846f9ceea27b98533a156c48dec204e9ec30f76dab78b81.
//
// Solidity: event OrderStored(address indexed swapper, uint256 indexed index, address tokenIn, address tokenOut, uint256 exchangeRate, uint256 deadline, bool OrderIsExecuted, bool isMultiPath, bytes encodedPath)
func (_ZDPc *ZDPcFilterer) ParseOrderStored(log types.Log) (*ZDPcOrderStored, error) {
	event := new(ZDPcOrderStored)
	if err := _ZDPc.contract.UnpackLog(event, "OrderStored", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcOwnershipTransferStartedIterator is returned from FilterOwnershipTransferStarted and is used to iterate over the raw logs and unpacked data for OwnershipTransferStarted events raised by the ZDPc contract.
type ZDPcOwnershipTransferStartedIterator struct {
	Event *ZDPcOwnershipTransferStarted // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcOwnershipTransferStartedIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcOwnershipTransferStarted)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcOwnershipTransferStarted)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcOwnershipTransferStartedIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcOwnershipTransferStartedIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcOwnershipTransferStarted represents a OwnershipTransferStarted event raised by the ZDPc contract.
type ZDPcOwnershipTransferStarted struct {
	PreviousOwner common.Address
	NewOwner      common.Address
	Raw           types.Log // Blockchain specific contextual infos
}

// FilterOwnershipTransferStarted is a free log retrieval operation binding the contract event 0x38d16b8cac22d99fc7c124b9cd0de2d3fa1faef420bfe791d8c362d765e22700.
//
// Solidity: event OwnershipTransferStarted(address indexed previousOwner, address indexed newOwner)
func (_ZDPc *ZDPcFilterer) FilterOwnershipTransferStarted(opts *bind.FilterOpts, previousOwner []common.Address, newOwner []common.Address) (*ZDPcOwnershipTransferStartedIterator, error) {

	var previousOwnerRule []interface{}
	for _, previousOwnerItem := range previousOwner {
		previousOwnerRule = append(previousOwnerRule, previousOwnerItem)
	}
	var newOwnerRule []interface{}
	for _, newOwnerItem := range newOwner {
		newOwnerRule = append(newOwnerRule, newOwnerItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "OwnershipTransferStarted", previousOwnerRule, newOwnerRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcOwnershipTransferStartedIterator{contract: _ZDPc.contract, event: "OwnershipTransferStarted", logs: logs, sub: sub}, nil
}

// WatchOwnershipTransferStarted is a free log subscription operation binding the contract event 0x38d16b8cac22d99fc7c124b9cd0de2d3fa1faef420bfe791d8c362d765e22700.
//
// Solidity: event OwnershipTransferStarted(address indexed previousOwner, address indexed newOwner)
func (_ZDPc *ZDPcFilterer) WatchOwnershipTransferStarted(opts *bind.WatchOpts, sink chan<- *ZDPcOwnershipTransferStarted, previousOwner []common.Address, newOwner []common.Address) (event.Subscription, error) {

	var previousOwnerRule []interface{}
	for _, previousOwnerItem := range previousOwner {
		previousOwnerRule = append(previousOwnerRule, previousOwnerItem)
	}
	var newOwnerRule []interface{}
	for _, newOwnerItem := range newOwner {
		newOwnerRule = append(newOwnerRule, newOwnerItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "OwnershipTransferStarted", previousOwnerRule, newOwnerRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcOwnershipTransferStarted)
				if err := _ZDPc.contract.UnpackLog(event, "OwnershipTransferStarted", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseOwnershipTransferStarted is a log parse operation binding the contract event 0x38d16b8cac22d99fc7c124b9cd0de2d3fa1faef420bfe791d8c362d765e22700.
//
// Solidity: event OwnershipTransferStarted(address indexed previousOwner, address indexed newOwner)
func (_ZDPc *ZDPcFilterer) ParseOwnershipTransferStarted(log types.Log) (*ZDPcOwnershipTransferStarted, error) {
	event := new(ZDPcOwnershipTransferStarted)
	if err := _ZDPc.contract.UnpackLog(event, "OwnershipTransferStarted", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcOwnershipTransferredIterator is returned from FilterOwnershipTransferred and is used to iterate over the raw logs and unpacked data for OwnershipTransferred events raised by the ZDPc contract.
type ZDPcOwnershipTransferredIterator struct {
	Event *ZDPcOwnershipTransferred // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcOwnershipTransferredIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcOwnershipTransferred)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcOwnershipTransferred)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcOwnershipTransferredIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcOwnershipTransferredIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcOwnershipTransferred represents a OwnershipTransferred event raised by the ZDPc contract.
type ZDPcOwnershipTransferred struct {
	PreviousOwner common.Address
	NewOwner      common.Address
	Raw           types.Log // Blockchain specific contextual infos
}

// FilterOwnershipTransferred is a free log retrieval operation binding the contract event 0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0.
//
// Solidity: event OwnershipTransferred(address indexed previousOwner, address indexed newOwner)
func (_ZDPc *ZDPcFilterer) FilterOwnershipTransferred(opts *bind.FilterOpts, previousOwner []common.Address, newOwner []common.Address) (*ZDPcOwnershipTransferredIterator, error) {

	var previousOwnerRule []interface{}
	for _, previousOwnerItem := range previousOwner {
		previousOwnerRule = append(previousOwnerRule, previousOwnerItem)
	}
	var newOwnerRule []interface{}
	for _, newOwnerItem := range newOwner {
		newOwnerRule = append(newOwnerRule, newOwnerItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "OwnershipTransferred", previousOwnerRule, newOwnerRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcOwnershipTransferredIterator{contract: _ZDPc.contract, event: "OwnershipTransferred", logs: logs, sub: sub}, nil
}

// WatchOwnershipTransferred is a free log subscription operation binding the contract event 0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0.
//
// Solidity: event OwnershipTransferred(address indexed previousOwner, address indexed newOwner)
func (_ZDPc *ZDPcFilterer) WatchOwnershipTransferred(opts *bind.WatchOpts, sink chan<- *ZDPcOwnershipTransferred, previousOwner []common.Address, newOwner []common.Address) (event.Subscription, error) {

	var previousOwnerRule []interface{}
	for _, previousOwnerItem := range previousOwner {
		previousOwnerRule = append(previousOwnerRule, previousOwnerItem)
	}
	var newOwnerRule []interface{}
	for _, newOwnerItem := range newOwner {
		newOwnerRule = append(newOwnerRule, newOwnerItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "OwnershipTransferred", previousOwnerRule, newOwnerRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcOwnershipTransferred)
				if err := _ZDPc.contract.UnpackLog(event, "OwnershipTransferred", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseOwnershipTransferred is a log parse operation binding the contract event 0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0.
//
// Solidity: event OwnershipTransferred(address indexed previousOwner, address indexed newOwner)
func (_ZDPc *ZDPcFilterer) ParseOwnershipTransferred(log types.Log) (*ZDPcOwnershipTransferred, error) {
	event := new(ZDPcOwnershipTransferred)
	if err := _ZDPc.contract.UnpackLog(event, "OwnershipTransferred", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcRouterChangedIterator is returned from FilterRouterChanged and is used to iterate over the raw logs and unpacked data for RouterChanged events raised by the ZDPc contract.
type ZDPcRouterChangedIterator struct {
	Event *ZDPcRouterChanged // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcRouterChangedIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcRouterChanged)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcRouterChanged)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcRouterChangedIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcRouterChangedIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcRouterChanged represents a RouterChanged event raised by the ZDPc contract.
type ZDPcRouterChanged struct {
	OldRouter common.Address
	NewRouter common.Address
	Raw       types.Log // Blockchain specific contextual infos
}

// FilterRouterChanged is a free log retrieval operation binding the contract event 0xc736654a613824c69968e0ec25ac1a428ccd49e15c28e97b5dfd2c6059757e2a.
//
// Solidity: event RouterChanged(address indexed oldRouter, address indexed newRouter)
func (_ZDPc *ZDPcFilterer) FilterRouterChanged(opts *bind.FilterOpts, oldRouter []common.Address, newRouter []common.Address) (*ZDPcRouterChangedIterator, error) {

	var oldRouterRule []interface{}
	for _, oldRouterItem := range oldRouter {
		oldRouterRule = append(oldRouterRule, oldRouterItem)
	}
	var newRouterRule []interface{}
	for _, newRouterItem := range newRouter {
		newRouterRule = append(newRouterRule, newRouterItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "RouterChanged", oldRouterRule, newRouterRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcRouterChangedIterator{contract: _ZDPc.contract, event: "RouterChanged", logs: logs, sub: sub}, nil
}

// WatchRouterChanged is a free log subscription operation binding the contract event 0xc736654a613824c69968e0ec25ac1a428ccd49e15c28e97b5dfd2c6059757e2a.
//
// Solidity: event RouterChanged(address indexed oldRouter, address indexed newRouter)
func (_ZDPc *ZDPcFilterer) WatchRouterChanged(opts *bind.WatchOpts, sink chan<- *ZDPcRouterChanged, oldRouter []common.Address, newRouter []common.Address) (event.Subscription, error) {

	var oldRouterRule []interface{}
	for _, oldRouterItem := range oldRouter {
		oldRouterRule = append(oldRouterRule, oldRouterItem)
	}
	var newRouterRule []interface{}
	for _, newRouterItem := range newRouter {
		newRouterRule = append(newRouterRule, newRouterItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "RouterChanged", oldRouterRule, newRouterRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcRouterChanged)
				if err := _ZDPc.contract.UnpackLog(event, "RouterChanged", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseRouterChanged is a log parse operation binding the contract event 0xc736654a613824c69968e0ec25ac1a428ccd49e15c28e97b5dfd2c6059757e2a.
//
// Solidity: event RouterChanged(address indexed oldRouter, address indexed newRouter)
func (_ZDPc *ZDPcFilterer) ParseRouterChanged(log types.Log) (*ZDPcRouterChanged, error) {
	event := new(ZDPcRouterChanged)
	if err := _ZDPc.contract.UnpackLog(event, "RouterChanged", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcTakenFeeWithdrawnIterator is returned from FilterTakenFeeWithdrawn and is used to iterate over the raw logs and unpacked data for TakenFeeWithdrawn events raised by the ZDPc contract.
type ZDPcTakenFeeWithdrawnIterator struct {
	Event *ZDPcTakenFeeWithdrawn // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcTakenFeeWithdrawnIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcTakenFeeWithdrawn)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcTakenFeeWithdrawn)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcTakenFeeWithdrawnIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcTakenFeeWithdrawnIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcTakenFeeWithdrawn represents a TakenFeeWithdrawn event raised by the ZDPc contract.
type ZDPcTakenFeeWithdrawn struct {
	Owner common.Address
	Fee   *big.Int
	Raw   types.Log // Blockchain specific contextual infos
}

// FilterTakenFeeWithdrawn is a free log retrieval operation binding the contract event 0x6b18e5ec1eb85e65aec1256ffdeead20d0d855853dfa10c96d4144d9310cf5ec.
//
// Solidity: event TakenFeeWithdrawn(address indexed owner, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) FilterTakenFeeWithdrawn(opts *bind.FilterOpts, owner []common.Address, fee []*big.Int) (*ZDPcTakenFeeWithdrawnIterator, error) {

	var ownerRule []interface{}
	for _, ownerItem := range owner {
		ownerRule = append(ownerRule, ownerItem)
	}
	var feeRule []interface{}
	for _, feeItem := range fee {
		feeRule = append(feeRule, feeItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "TakenFeeWithdrawn", ownerRule, feeRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcTakenFeeWithdrawnIterator{contract: _ZDPc.contract, event: "TakenFeeWithdrawn", logs: logs, sub: sub}, nil
}

// WatchTakenFeeWithdrawn is a free log subscription operation binding the contract event 0x6b18e5ec1eb85e65aec1256ffdeead20d0d855853dfa10c96d4144d9310cf5ec.
//
// Solidity: event TakenFeeWithdrawn(address indexed owner, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) WatchTakenFeeWithdrawn(opts *bind.WatchOpts, sink chan<- *ZDPcTakenFeeWithdrawn, owner []common.Address, fee []*big.Int) (event.Subscription, error) {

	var ownerRule []interface{}
	for _, ownerItem := range owner {
		ownerRule = append(ownerRule, ownerItem)
	}
	var feeRule []interface{}
	for _, feeItem := range fee {
		feeRule = append(feeRule, feeItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "TakenFeeWithdrawn", ownerRule, feeRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcTakenFeeWithdrawn)
				if err := _ZDPc.contract.UnpackLog(event, "TakenFeeWithdrawn", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseTakenFeeWithdrawn is a log parse operation binding the contract event 0x6b18e5ec1eb85e65aec1256ffdeead20d0d855853dfa10c96d4144d9310cf5ec.
//
// Solidity: event TakenFeeWithdrawn(address indexed owner, uint256 indexed fee)
func (_ZDPc *ZDPcFilterer) ParseTakenFeeWithdrawn(log types.Log) (*ZDPcTakenFeeWithdrawn, error) {
	event := new(ZDPcTakenFeeWithdrawn)
	if err := _ZDPc.contract.UnpackLog(event, "TakenFeeWithdrawn", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}

// ZDPcVerifierChangedIterator is returned from FilterVerifierChanged and is used to iterate over the raw logs and unpacked data for VerifierChanged events raised by the ZDPc contract.
type ZDPcVerifierChangedIterator struct {
	Event *ZDPcVerifierChanged // Event containing the contract specifics and raw log

	contract *bind.BoundContract // Generic contract to use for unpacking event data
	event    string              // Event name to use for unpacking event data

	logs chan types.Log        // Log channel receiving the found contract events
	sub  ethereum.Subscription // Subscription for errors, completion and termination
	done bool                  // Whether the subscription completed delivering logs
	fail error                 // Occurred error to stop iteration
}

// Next advances the iterator to the subsequent event, returning whether there
// are any more events found. In case of a retrieval or parsing error, false is
// returned and Error() can be queried for the exact failure.
func (it *ZDPcVerifierChangedIterator) Next() bool {
	// If the iterator failed, stop iterating
	if it.fail != nil {
		return false
	}
	// If the iterator completed, deliver directly whatever's available
	if it.done {
		select {
		case log := <-it.logs:
			it.Event = new(ZDPcVerifierChanged)
			if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
				it.fail = err
				return false
			}
			it.Event.Raw = log
			return true

		default:
			return false
		}
	}
	// Iterator still in progress, wait for either a data or an error event
	select {
	case log := <-it.logs:
		it.Event = new(ZDPcVerifierChanged)
		if err := it.contract.UnpackLog(it.Event, it.event, log); err != nil {
			it.fail = err
			return false
		}
		it.Event.Raw = log
		return true

	case err := <-it.sub.Err():
		it.done = true
		it.fail = err
		return it.Next()
	}
}

// Error returns any retrieval or parsing error occurred during filtering.
func (it *ZDPcVerifierChangedIterator) Error() error {
	return it.fail
}

// Close terminates the iteration process, releasing any pending underlying
// resources.
func (it *ZDPcVerifierChangedIterator) Close() error {
	it.sub.Unsubscribe()
	return nil
}

// ZDPcVerifierChanged represents a VerifierChanged event raised by the ZDPc contract.
type ZDPcVerifierChanged struct {
	OldVerifier common.Address
	NewVerifier common.Address
	Raw         types.Log // Blockchain specific contextual infos
}

// FilterVerifierChanged is a free log retrieval operation binding the contract event 0x0ddda8be1021ab00f63727c5c5504ad96b163269770a3fe8ac3dd0bcb40208df.
//
// Solidity: event VerifierChanged(address indexed oldVerifier, address indexed newVerifier)
func (_ZDPc *ZDPcFilterer) FilterVerifierChanged(opts *bind.FilterOpts, oldVerifier []common.Address, newVerifier []common.Address) (*ZDPcVerifierChangedIterator, error) {

	var oldVerifierRule []interface{}
	for _, oldVerifierItem := range oldVerifier {
		oldVerifierRule = append(oldVerifierRule, oldVerifierItem)
	}
	var newVerifierRule []interface{}
	for _, newVerifierItem := range newVerifier {
		newVerifierRule = append(newVerifierRule, newVerifierItem)
	}

	logs, sub, err := _ZDPc.contract.FilterLogs(opts, "VerifierChanged", oldVerifierRule, newVerifierRule)
	if err != nil {
		return nil, err
	}
	return &ZDPcVerifierChangedIterator{contract: _ZDPc.contract, event: "VerifierChanged", logs: logs, sub: sub}, nil
}

// WatchVerifierChanged is a free log subscription operation binding the contract event 0x0ddda8be1021ab00f63727c5c5504ad96b163269770a3fe8ac3dd0bcb40208df.
//
// Solidity: event VerifierChanged(address indexed oldVerifier, address indexed newVerifier)
func (_ZDPc *ZDPcFilterer) WatchVerifierChanged(opts *bind.WatchOpts, sink chan<- *ZDPcVerifierChanged, oldVerifier []common.Address, newVerifier []common.Address) (event.Subscription, error) {

	var oldVerifierRule []interface{}
	for _, oldVerifierItem := range oldVerifier {
		oldVerifierRule = append(oldVerifierRule, oldVerifierItem)
	}
	var newVerifierRule []interface{}
	for _, newVerifierItem := range newVerifier {
		newVerifierRule = append(newVerifierRule, newVerifierItem)
	}

	logs, sub, err := _ZDPc.contract.WatchLogs(opts, "VerifierChanged", oldVerifierRule, newVerifierRule)
	if err != nil {
		return nil, err
	}
	return event.NewSubscription(func(quit <-chan struct{}) error {
		defer sub.Unsubscribe()
		for {
			select {
			case log := <-logs:
				// New log arrived, parse the event and forward to the user
				event := new(ZDPcVerifierChanged)
				if err := _ZDPc.contract.UnpackLog(event, "VerifierChanged", log); err != nil {
					return err
				}
				event.Raw = log

				select {
				case sink <- event:
				case err := <-sub.Err():
					return err
				case <-quit:
					return nil
				}
			case err := <-sub.Err():
				return err
			case <-quit:
				return nil
			}
		}
	}), nil
}

// ParseVerifierChanged is a log parse operation binding the contract event 0x0ddda8be1021ab00f63727c5c5504ad96b163269770a3fe8ac3dd0bcb40208df.
//
// Solidity: event VerifierChanged(address indexed oldVerifier, address indexed newVerifier)
func (_ZDPc *ZDPcFilterer) ParseVerifierChanged(log types.Log) (*ZDPcVerifierChanged, error) {
	event := new(ZDPcVerifierChanged)
	if err := _ZDPc.contract.UnpackLog(event, "VerifierChanged", log); err != nil {
		return nil, err
	}
	event.Raw = log
	return event, nil
}
