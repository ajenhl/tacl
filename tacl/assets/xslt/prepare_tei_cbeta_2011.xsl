<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet extension-element-prefixes="fn my str"
                version="1.0"
                xmlns:cb="http://www.cbeta.org/ns/1.0"
                xmlns:fn="http://exslt.org/functions"
                xmlns:my="urn:foo"
                xmlns:str="http://exslt.org/strings"
                xmlns:tei="http://www.tei-c.org/ns/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output encoding="UTF-8" method="xml" />

  <xsl:strip-space elements="*" />

  <xsl:template match="div1|div2">
    <cb:div>
      <xsl:apply-templates select="@*|node()" />
    </cb:div>
  </xsl:template>

  <xsl:template match="gaiji">
    <xsl:choose>
      <xsl:when test="@des">
        <xsl:value-of select="@des" />
      </xsl:when>
      <xsl:when test="@uni">
        <xsl:value-of select="my:decode-codepoint(@uni)" />
      </xsl:when>
      <xsl:when test="@udia">
        <xsl:value-of select="@udia" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>GAIJI WITHOUT REPRESENTATION</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="head[@type='no']">
    <cb:docNumber>
      <xsl:apply-templates select="node()" />
    </cb:docNumber>
  </xsl:template>

  <xsl:template match="jhead">
    <cb:jhead>
      <xsl:apply-templates select="@*|node()" />
    </cb:jhead>
  </xsl:template>

  <xsl:template match="juan">
    <cb:juan>
      <xsl:apply-templates select="@*|node()" />
    </cb:juan>
  </xsl:template>

  <xsl:template match="lem/@wit" />

  <xsl:template match="mulu">
    <cb:mulu>
      <xsl:apply-templates select="@*|node()" />
    </cb:mulu>
  </xsl:template>

  <xsl:template match="t/@lang[.='chi']">
    <xsl:attribute name="xml:lang">
      <xsl:text>zh</xsl:text>
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="TEI.2">
    <tei:TEI>
      <xsl:apply-templates select="@*|node()" />
    </tei:TEI>
  </xsl:template>

  <xsl:template match="language/@id">
    <xsl:attribute name="ident">
      <xsl:value-of select="." />
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="@id">
    <xsl:attribute name="xml:id">
      <xsl:value-of select="." />
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="@lang">
    <xsl:attribute name="xml:lang">
      <xsl:value-of select="." />
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="mulu/@label" />

  <xsl:template match="p/@place">
    <xsl:attribute name="rend">
      <xsl:value-of select="." />
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="byline/@type | p/@type">
    <xsl:attribute name="cb:type">
      <xsl:value-of select="." />
    </xsl:attribute>
  </xsl:template>

  <xsl:template match="*">
    <xsl:element name="{local-name()}" namespace="http://www.tei-c.org/ns/1.0">
      <xsl:apply-templates select="@*|node()" />
    </xsl:element>
  </xsl:template>

  <xsl:template match="@*">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()" />
    </xsl:copy>
  </xsl:template>

  <xsl:template match="node()" priority="-1">
    <xsl:copy>
      <xsl:apply-templates select="node()" />
    </xsl:copy>
  </xsl:template>

  <!-- The following functions are by Aristotle Pagaltzis, from
       http://plasmasturm.org/log/386/ -->
  <fn:function name="my:hex2num">
    <xsl:param name="hexstr" />
    <xsl:variable name="head"
                  select="substring( $hexstr, 1, string-length( $hexstr ) - 1 )"
    />
    <xsl:variable name="nybble"
                  select="substring( $hexstr, string-length( $hexstr ) )" />
    <xsl:choose>
      <xsl:when test="string-length( $hexstr ) = 0">
        <fn:result select="0" />
      </xsl:when>
      <xsl:when test="string( number( $nybble ) ) = 'NaN'">
        <fn:result select="
          my:hex2num( $head ) * 16
          + number( concat( 1, translate( $nybble, 'ABCDEF', '012345' ) ) )
        "/>
      </xsl:when>
      <xsl:otherwise>
        <fn:result select="my:hex2num( $head ) * 16 + number( $nybble )" />
      </xsl:otherwise>
    </xsl:choose>
  </fn:function>
  <fn:function name="my:num2hex">
    <xsl:param name="num" />
    <xsl:variable name="nybble" select="$num mod 16" />
    <xsl:variable name="head" select="floor( $num div 16 )" />
    <xsl:variable name="rest">
      <xsl:if test="not( $head = 0 )">
        <xsl:value-of select="my:num2hex( $head )"/>
      </xsl:if>
    </xsl:variable>
    <xsl:choose>
      <xsl:when test="$nybble > 9">
        <fn:result select="concat(
          $rest,
          translate( substring( $nybble, 2 ), '012345', 'ABCDEF' )
        )"/>
      </xsl:when>
      <xsl:otherwise>
        <fn:result select="concat( $rest, $nybble )" />
      </xsl:otherwise>
    </xsl:choose>
  </fn:function>
  <fn:function name="my:char-to-utf8bytes">
    <xsl:param name="codepoint" />
    <xsl:choose>
      <xsl:when test="$codepoint > 65536">
        <fn:result select="
            ( ( floor( $codepoint div 262144 ) mod  8 + 240 ) * 16777216 )
          + ( ( floor( $codepoint div   4096 ) mod 64 + 128 ) *    65536 )
          + ( ( floor( $codepoint div     64 ) mod 64 + 128 ) *      256 )
          + ( ( floor( $codepoint div      1 ) mod 64 + 128 ) *        1 )
        " />
      </xsl:when>
      <xsl:when test="$codepoint > 2048">
        <fn:result select="
            ( ( floor( $codepoint div   4096 ) mod 16 + 224 ) *    65536 )
          + ( ( floor( $codepoint div     64 ) mod 64 + 128 ) *      256 )
          + ( ( floor( $codepoint div      1 ) mod 64 + 128 ) *        1 )
        " />
      </xsl:when>
      <xsl:when test="$codepoint > 128">
        <fn:result select="
            ( ( floor( $codepoint div     64 ) mod 32 + 192 ) *      256 )
          + ( ( floor( $codepoint div      1 ) mod 64 + 128 ) *        1 )
        " />
      </xsl:when>
      <xsl:otherwise>
        <fn:result select="$codepoint" />
      </xsl:otherwise>
    </xsl:choose>
  </fn:function>
  <fn:function name="my:percentify">
    <xsl:param name="str" />
    <xsl:choose>
      <xsl:when test="string-length( $str ) > 2">
        <fn:result select="concat(
          '%',
          substring( $str, 1, 2 ),
          my:percentify( substring( $str, 3 ) )
        )" />
      </xsl:when>
      <xsl:otherwise>
        <fn:result select="concat( '%', $str )" />
      </xsl:otherwise>
    </xsl:choose>
  </fn:function>
  <fn:function name="my:decode-codepoint">
    <xsl:param name="codepoint" />
    <fn:result
      select="str:decode-uri( my:percentify(
        my:num2hex( my:char-to-utf8bytes(
          my:hex2num( $codepoint )
        ) )
      ) )"
    />
  </fn:function>

</xsl:stylesheet>
