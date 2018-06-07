package main

import (
	"time"
)

const (
	ParseResultSucess = iota
	ParseResultNotComplete
	ParseResultError
	ParseResultBadPrefix
)

type IPacket interface {
	ReceivedTime() time.Time
	Buffer() []byte
}
